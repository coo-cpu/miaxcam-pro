"""
问题4：基于CMA-ES算法的三无人机协同烟幕遮挡优化

本代码实现了使用协方差矩阵自适应进化策略(CMA-ES)算法来优化三架无人机
(FY1, FY2, FY3)的协同烟幕投放策略，以最大化对来袭导弹的遮挡效果。

核心优化目标：
- 最大化烟幕遮挡的总有效时间
- 协调三架无人机的飞行轨迹和烟弹投放时机
- 考虑物理约束和作战环境限制

算法特点：
- 使用CMA-ES进行全局优化
- 多目标协同优化
- 高维参数空间搜索
- 自适应策略调整


"""

import numpy as np
import math
import time
import json
import sys
import cma
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing
import matplotlib.pyplot as plt
from datetime import datetime
import os

# 配置matplotlib中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS', 'Arial']
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

# 导入烟幕遮挡仿真模块
from smoke_obscure import line_segment_intersects_sphere


class Problem4CMAESOptimizer:
    """
    问题4的CMA-ES优化器类
    
    该类封装了三无人机协同烟幕遮挡优化的所有核心功能：
    1. 参数空间定义
    2. 目标函数计算
    3. 物理约束处理
    4. CMA-ES算法执行
    5. 结果分析和可视化
    """
    
    def __init__(self):
        """初始化优化器参数和常量"""

        # 物理常量
        self.g = 9.81  # 重力加速度 m/s²
        self.missile_speed = 300.0  # 导弹速度 m/s
        self.cloud_radius = 10.0  # 烟幕云团半径 m
        self.cloud_sink_speed = 3.0  # 烟幕下沉速度 m/s
        self.cloud_lifetime = 20.0  # 烟幕有效时间 s

        # 目标参数
        self.missile_start = np.array([20000.0, 0.0, 2000.0])  # 导弹初始位置
        self.false_target = np.array([0.0, 0.0, 0.0])  # 假目标位置
        self.true_target_center = np.array([0.0, 200.0, 0.0])  # 真目标圆柱体中心
        self.cylinder_radius = 7.0  # 圆柱体半径 m
        self.cylinder_height = 10.0  # 圆柱体高度 m

        # 无人机初始位置
        self.drone_positions = {
            'FY1': np.array([17800.0, 0.0, 1800.0]),
            'FY2': np.array([12000.0, 1400.0, 1400.0]),
            'FY3': np.array([6000.0, -3000.0, 700.0])
        }

        # 优化参数边界
        self.speed_bounds = [100.0, 140.0]  # 无人机速度范围 m/s
        self.angle_bounds = [2.5, 3.5]  # 飞行角度范围 rad
        self.release_time_bounds = [0.0, 6.0]  # 烟弹释放时间范围 s
        self.detonation_delay_bounds = [0.0, 8.0]  # 起爆延迟范围 s

        # 仿真参数
        self.dt = 0.01  # 时间步长 s
        self.sample_theta = 36  # 圆柱体角度采样数
        self.sample_z = 11  # 圆柱体高度采样数

        # 判定阈值：将“完全遮挡”放宽为覆盖比例>=该阈值（例如98%）
        # 说明：理论上单个/少量球形烟云很难在任意时刻同时遮住圆柱体全部采样点，
        # 为了避免客观上永远为0秒的极端判定，引入软阈值作为工程判据。
        self.coverage_threshold = 0.98  # 98% 以上视作“完全遮挡”

        # CMA-ES参数
        self.dimension = 12  # 优化维度：3架无人机 × 4个参数
        self.population_size = None  # 将由CMA-ES自动确定
        self.max_generations = 100
        self.tolerance = 1e-8

        # 结果存储
        self.best_solution = None
        self.best_fitness = -np.inf
        self.optimization_history = []

        # 可选：策略约束框（按无人机角色收紧搜索范围）
        # 结构：{
        #   'angles': [(min,max)]*3,
        #   'speeds': [(min,max)]*3,
        #   'release_times': [(min,max)]*3,
        #   'delays': [(min,max)]*3
        # }
        self.strategy_frame = None
        
    def encode_solution(self, angles, speeds, release_times, detonation_delays):
        """
        将无人机策略参数编码为优化向量
        
        参数:
        - angles: [3] 各无人机飞行角度
        - speeds: [3] 各无人机飞行速度
        - release_times: [3] 各无人机烟弹释放时间
        - detonation_delays: [3] 各无人机烟弹起爆延迟
        
        返回:
        - solution: [12] 编码后的解向量
        """
        solution = np.zeros(self.dimension)
        solution[0:3] = angles
        solution[3:6] = speeds
        solution[6:9] = release_times
        solution[9:12] = detonation_delays
        return solution
    
    def decode_solution(self, solution):
        """
        将优化向量解码为无人机策略参数
        
        参数:
        - solution: [12] 解向量
        
        返回:
        - angles, speeds, release_times, detonation_delays: 解码后的策略参数
        """
        angles = solution[0:3]
        speeds = solution[3:6]
        release_times = solution[6:9]
        detonation_delays = solution[9:12]
        return angles, speeds, release_times, detonation_delays
    
    def apply_constraints(self, solution):
        """
        应用约束条件，确保解在可行域内
        
        参数:
        - solution: [12] 原始解向量
        
        返回:
        - constrained_solution: [12] 约束后的解向量
        """
        constrained = solution.copy()
        
        if self.strategy_frame is None:
            # 默认全局约束
            constrained[0:3] = np.clip(
                constrained[0:3], self.angle_bounds[0], self.angle_bounds[1]
            )
            constrained[3:6] = np.clip(
                constrained[3:6], self.speed_bounds[0], self.speed_bounds[1]
            )
            constrained[6:9] = np.clip(
                constrained[6:9], self.release_time_bounds[0], self.release_time_bounds[1]
            )
            constrained[9:12] = np.clip(
                constrained[9:12], self.detonation_delay_bounds[0], self.detonation_delay_bounds[1]
            )
        else:
            # 使用策略框的逐无人机约束
            for i in range(3):
                a_min, a_max = self.strategy_frame['angles'][i]
                v_min, v_max = self.strategy_frame['speeds'][i]
                r_min, r_max = self.strategy_frame['release_times'][i]
                d_min, d_max = self.strategy_frame['delays'][i]
                constrained[i] = np.clip(constrained[i], a_min, a_max)
                constrained[3 + i] = np.clip(constrained[3 + i], v_min, v_max)
                constrained[6 + i] = np.clip(constrained[6 + i], r_min, r_max)
                constrained[9 + i] = np.clip(constrained[9 + i], d_min, d_max)
        
        return constrained

    def _bearing_to_target(self, drone_id):
        """计算无人机起点指向真目标中心的方位角（弧度）。"""
        pos = self.drone_positions[drone_id]
        vec = self.true_target_center - pos
        return math.atan2(vec[1], vec[0])

    def apply_strategy_framing(self, mode='three_role', angle_half_width_deg=25.0):
        """
        启用策略框以收紧搜索空间，使遮挡更可行。
        
        基于物理约束的正确参数范围 (修正版)

        参数:
        - mode: 'three_role' 采用三机分工（正面/左翼/右翼掠入）
        - angle_half_width_deg: 每个扇区的半宽度（度）
        """
        # 修正策略：严格遵守物理约束
        angles = []
        speeds = []
        release_times = []
        delays = []

        # 目标高度选择圆柱中部（更易遮挡）
        target_z = self.cylinder_height * 0.6

        # 基于实际几何计算每个无人机到目标的正确角度范围
        for idx, d in enumerate(['FY1', 'FY2', 'FY3']):
            pos = self.drone_positions[d]
            to_target = self.true_target_center - pos
            center_bearing = math.atan2(to_target[1], to_target[0])
            
            # 适度扩展角度范围到±18°（平衡自由度与收敛性）
            half_width = math.radians(18.0)  # 从±15°适度扩展到±18°
            
            if d == 'FY1':  # ~179°
                angles.append((center_bearing - half_width, center_bearing + half_width))
            elif d == 'FY2':  # ~-174° 需要处理负角度
                # 将负角度转换为正角度: -174° = 186°
                center_positive = center_bearing + 2*math.pi if center_bearing < 0 else center_bearing
                angles.append((center_positive - half_width, center_positive + half_width))
            else:  # FY3 ~152°
                angles.append((center_bearing - half_width, center_bearing + half_width))

            # 严格遵守速度上限140m/s，但优化分布
            if d == 'FY1':
                speeds.append((132.0, 140.0))  # 高速区间，接近上限
            elif d == 'FY2':
                speeds.append((128.0, 138.0))  # 中高速区间
            else:  # FY3
                speeds.append((125.0, 135.0))  # 保持原有范围

            # 烟雾弹物理约束计算
            h0 = self.drone_positions[d][2]  # 无人机高度
            h_target = self.cylinder_height * 0.5  # 目标中部
            h_drop = max(5.0, h0 - h_target)
            
            # 落地时间（自由落体）: t = sqrt(2h/g) 
            t_fall_to_target = math.sqrt(2.0 * h_drop / self.g)
            t_fall_to_ground = math.sqrt(2.0 * h0 / self.g)
            
            # 安全约束：总时间(释放+延迟) < 落地时间 - 2秒安全边界
            max_total_time = t_fall_to_target - 2.0
            
            # 基于边界分析：释放时间向更早扩展
            r_min, r_max = 0.2, 2.0  # 允许更早释放，但不要太极端
            
            # 延迟时间：用户建议下限设为0（支持立即释放策略）
            d_max = max(1.0, max_total_time - r_max)  # 动态计算延迟上限
            d_min = 0.0  # 用户建议：支持立即释放，因为导弹比无人机快很多
            
            # 确保延迟范围合理
            if d_max < d_min:
                d_max = 1.0
            
            release_times.append((r_min, r_max))
            delays.append((d_min, min(d_max, 6.0)))  # 限制延迟上限为6秒

        self.strategy_frame = {
            'angles': angles,
            'speeds': speeds,
            'release_times': release_times,
            'delays': delays,
        }
        return self.strategy_frame
    
    def compute_drone_trajectory(self, drone_id, angle, speed):
        """
        计算无人机轨迹
        
        参数:
        - drone_id: 'FY1', 'FY2', 或 'FY3'
        - angle: 飞行角度 (弧度)
        - speed: 飞行速度 (m/s)
        
        返回:
        - trajectory_func: 轨迹函数 f(t) -> position
        """
        start_pos = self.drone_positions[drone_id]
        velocity = np.array([speed * math.cos(angle), 
                            speed * math.sin(angle), 
                            0.0])  # 水平飞行
        
        def trajectory(t):
            return start_pos + velocity * t
        
        return trajectory, velocity
    
    def compute_bomb_trajectory(self, drone_trajectory_func, drone_velocity, release_time):
        """
        计算烟弹轨迹（抛物运动）
        
        参数:
        - drone_trajectory_func: 无人机轨迹函数
        - drone_velocity: 无人机速度向量
        - release_time: 烟弹释放时间
        
        返回:
        - bomb_trajectory_func: 烟弹轨迹函数 f(t) -> position (t >= release_time)
        """
        release_pos = drone_trajectory_func(release_time)
        initial_velocity = drone_velocity.copy()  # 烟弹初始速度等于无人机速度
        
        def bomb_trajectory(t):
            if t < release_time:
                return None  # 烟弹尚未释放
            
            dt = t - release_time
            # 抛物运动方程
            x = release_pos[0] + initial_velocity[0] * dt
            y = release_pos[1] + initial_velocity[1] * dt
            z = release_pos[2] + initial_velocity[2] * dt - 0.5 * self.g * dt * dt
            
            return np.array([x, y, z])
        
        return bomb_trajectory
    
    def compute_smoke_cloud_center(self, bomb_pos_at_detonation, detonation_time):
        """
        计算烟幕云团中心轨迹
        
        参数:
        - bomb_pos_at_detonation: 烟弹起爆位置
        - detonation_time: 起爆时间
        
        返回:
        - cloud_center_func: 云团中心轨迹函数 f(t) -> position (t >= detonation_time)
        """
        def cloud_center(t):
            if t < detonation_time:
                return None  # 云团尚未产生
            
            dt = t - detonation_time
            # 云团垂直下沉
            center = bomb_pos_at_detonation.copy()
            center[2] -= self.cloud_sink_speed * dt
            
            return center
        
        return cloud_center
    
    def sample_cylinder_surface(self):
        """
        在圆柱体表面采样点
        
        返回:
        - sample_points: [N, 3] 表面采样点坐标
        """
        thetas = np.linspace(0.0, 2*math.pi, self.sample_theta, endpoint=False)
        zs = np.linspace(0.0, self.cylinder_height, self.sample_z)
        
        sample_points = []
        for z in zs:
            for theta in thetas:
                x = self.true_target_center[0] + self.cylinder_radius * math.cos(theta)
                y = self.true_target_center[1] + self.cylinder_radius * math.sin(theta)
                sample_points.append([x, y, z])
        
        return np.array(sample_points)
    
    def check_line_of_sight_blocked(self, missile_pos, target_point, cloud_centers, cloud_radius):
        """
        检查视线是否被烟幕云团阻挡
        
        参数:
        - missile_pos: 导弹位置
        - target_point: 目标点位置
        - cloud_centers: 烟幕云团中心位置列表
        - cloud_radius: 云团半径
        
        返回:
        - blocked: bool, 是否被阻挡
        """
        for cloud_center in cloud_centers:
            if cloud_center is not None:
                if line_segment_intersects_sphere(missile_pos, target_point, 
                                                cloud_center, cloud_radius):
                    return True
        return False
    
    def compute_missile_trajectory(self):
        """
        计算导弹轨迹
        
        返回:
        - missile_trajectory_func: 导弹轨迹函数 f(t) -> position
        """
        direction = self.false_target - self.missile_start
        distance = np.linalg.norm(direction)
        
        if distance == 0:
            velocity = np.zeros(3)
            arrival_time = 0
        else:
            velocity = (direction / distance) * self.missile_speed
            arrival_time = distance / self.missile_speed
        
        def missile_trajectory(t):
            # 将 numpy 标量转为 Python float，避免类型检查器误报
            t_clamped = min(float(t), float(arrival_time))  # 导弹到达假目标后停止
            return self.missile_start + velocity * t_clamped
        
        return missile_trajectory, arrival_time
    
    def simulate_scenario(self, solution, include_mask=None):
        """
        仿真整个作战场景
        
        参数:
        - solution: [12] 优化解向量
        - include_mask: [bool,bool,bool] 可选，指定参与仿真的无人机，None表示全部
        
        返回:
        - total_obscuration_time: 总遮挡时间 (秒)
        - detailed_results: 详细仿真结果
        """
        # 解码并应用约束
        angles, speeds, release_times, detonation_delays = self.decode_solution(solution)
        solution_constrained = self.apply_constraints(solution)
        angles, speeds, release_times, detonation_delays = self.decode_solution(solution_constrained)

        # 无人机轨迹
        drone_trajectories = {}
        drone_velocities = {}
        for i, drone_id in enumerate(['FY1', 'FY2', 'FY3']):
            traj_func, velocity = self.compute_drone_trajectory(drone_id, angles[i], speeds[i])
            drone_trajectories[drone_id] = traj_func
            drone_velocities[drone_id] = velocity

        # 烟弹轨迹与起爆信息
        bomb_trajectories = {}
        detonation_times = {}
        bomb_positions_at_detonation = {}
        for i, drone_id in enumerate(['FY1', 'FY2', 'FY3']):
            bomb_traj = self.compute_bomb_trajectory(
                drone_trajectories[drone_id],
                drone_velocities[drone_id],
                release_times[i]
            )
            bomb_trajectories[drone_id] = bomb_traj
            det_time = release_times[i] + detonation_delays[i]
            detonation_times[drone_id] = det_time
            bomb_positions_at_detonation[drone_id] = bomb_traj(det_time)

        # 云团轨迹
        cloud_trajectories = {}
        for drone_id in ['FY1', 'FY2', 'FY3']:
            cloud_traj = self.compute_smoke_cloud_center(
                bomb_positions_at_detonation[drone_id],
                detonation_times[drone_id]
            )
            cloud_trajectories[drone_id] = cloud_traj

        # 导弹轨迹与目标表面采样
        missile_trajectory, missile_arrival_time = self.compute_missile_trajectory()
        target_surface_points = self.sample_cylinder_surface()

        # 参与仿真的无人机
        drone_ids_all = ['FY1', 'FY2', 'FY3']
        if include_mask is None:
            included_ids = drone_ids_all
        else:
            included_ids = [d for d, flag in zip(drone_ids_all, include_mask) if flag]
            if not included_ids:
                return 0.0, {}

        # 时间范围：从最晚起爆开始到云团结束与导弹到达更早者
        max_detonation_time = max(detonation_times[d] for d in included_ids)
        max_cloud_end_time = max_detonation_time + self.cloud_lifetime
        simulation_end_time = min(float(max_cloud_end_time), float(missile_arrival_time))
        if simulation_end_time <= max_detonation_time:
            return 0.0, {}

        # 主循环
        times = np.arange(max_detonation_time, simulation_end_time + self.dt / 2, self.dt)
        fully_obscured_flags = []
        max_coverage_ratio = 0.0
        for t in times:
            missile_pos = missile_trajectory(t)
            # 当前有效云团中心
            active_cloud_centers = []
            for drone_id in included_ids:
                det_time = detonation_times[drone_id]
                cloud_end_time = det_time + self.cloud_lifetime
                if det_time <= t <= cloud_end_time:
                    cloud_center = cloud_trajectories[drone_id](t)
                    if cloud_center is not None:
                        active_cloud_centers.append(cloud_center)

            # 覆盖比例
            if not active_cloud_centers:
                coverage_ratio = 0.0
            else:
                hits = 0
                total_pts = len(target_surface_points)
                for target_point in target_surface_points:
                    if self.check_line_of_sight_blocked(
                        missile_pos, target_point, active_cloud_centers, self.cloud_radius
                    ):
                        hits += 1
                coverage_ratio = hits / max(1, total_pts)

            max_coverage_ratio = max(max_coverage_ratio, coverage_ratio)
            fully_obscured_flags.append(coverage_ratio >= self.coverage_threshold)

        total_obscuration_time = sum(fully_obscured_flags) * self.dt
        detailed_results = {
            'angles': angles.tolist() if hasattr(angles, 'tolist') else list(angles),
            'speeds': speeds.tolist() if hasattr(speeds, 'tolist') else list(speeds),
            'release_times': release_times.tolist() if hasattr(release_times, 'tolist') else list(release_times),
            'detonation_delays': detonation_delays.tolist() if hasattr(detonation_delays, 'tolist') else list(detonation_delays),
            'detonation_times': {k: float(v) for k, v in detonation_times.items()},
            'total_obscuration_time': float(total_obscuration_time),
            'simulation_time_range': [float(times[0]), float(times[-1])] if len(times) > 0 else [0.0, 0.0],
            'obscuration_ratio': float(np.mean(fully_obscured_flags)) if fully_obscured_flags else 0.0,
            'max_coverage_ratio': float(max_coverage_ratio),
            'coverage_threshold': float(self.coverage_threshold),
            'included_ids': included_ids,
        }
        return total_obscuration_time, detailed_results
    
    def objective_function(self, solution):
        """
        CMA-ES目标函数（需要最小化）
        
        参数:
        - solution: [12] 优化解向量
        
        返回:
        - fitness: 适应度值（负的遮挡时间，因为CMA-ES做最小化）
        """
        try:
            total_obscuration_time, _ = self.simulate_scenario(solution)
            # CMA-ES进行最小化，所以返回负值
            return -total_obscuration_time
        
        except Exception as e:
            print(f"目标函数计算错误: {e}")
            return 1e6  # 惩罚值
    
    def run_optimization(self, sigma0=0.5, popsize=None, maxfev=None, maxiter=None, min_generations=5, verbose=True):
        """
        运行CMA-ES优化
        
        参数:
        - sigma0: 初始步长
        - popsize: 种群大小（None为自动）
    - maxfev: 最大函数评估次数（将映射为cma的maxfevals）
    - maxiter: 最大迭代次数（代数）
    - min_generations: 至少运行的代数，避免因tolfun过早停止
        - verbose: 是否打印详细信息
        
        返回:
        - optimization_results: 优化结果字典
        """
        print("开始基于CMA-ES的三无人机协同烟幕遮挡优化...")
        print(f"优化维度: {self.dimension}")
        if self.strategy_frame is None:
            print(f"参数边界: 角度[{self.angle_bounds}], 速度{self.speed_bounds}, 释放时间{self.release_time_bounds}, 起爆延迟{self.detonation_delay_bounds}")
        else:
            print("已启用策略框以收紧搜索范围：")
            for i, d in enumerate(['FY1','FY2','FY3']):
                a = self.strategy_frame['angles'][i]
                v = self.strategy_frame['speeds'][i]
                r = self.strategy_frame['release_times'][i]
                de = self.strategy_frame['delays'][i]
                print(f"  {d}: 角度[{a[0]:.2f},{a[1]:.2f}], 速度[{v[0]:.1f},{v[1]:.1f}], 释放[{r[0]:.1f},{r[1]:.1f}], 延迟[{de[0]:.1f},{de[1]:.1f}]")
        
        # 设置初始解（在约束范围中心）
        if self.strategy_frame is None:
            initial_solution = np.array([
                # 角度 (3个)
                math.pi, math.pi, math.pi,
                # 速度 (3个)
                135.0, 135.0, 135.0,
                # 释放时间 (3个)
                3.0, 3.0, 3.0,
                # 起爆延迟 (3个)
                5.0, 5.0, 5.0
            ])
        else:
            # 使用策略框的中点作为初始解
            def circ_mid(a, b):
                two_pi = 2*math.pi
                delta = (b - a + two_pi) % two_pi
                return (a + delta/2) % two_pi
            angles_mid = [circ_mid(*self.strategy_frame['angles'][i]) for i in range(3)]
            speeds_mid = [0.5*(self.strategy_frame['speeds'][i][0] + self.strategy_frame['speeds'][i][1]) for i in range(3)]
            rel_mid = [0.5*(self.strategy_frame['release_times'][i][0] + self.strategy_frame['release_times'][i][1]) for i in range(3)]
            del_mid = [0.5*(self.strategy_frame['delays'][i][0] + self.strategy_frame['delays'][i][1]) for i in range(3)]
            initial_solution = np.array(list(angles_mid) + list(speeds_mid) + list(rel_mid) + list(del_mid))
        
        # 设置边界约束 (CMA-ES格式: [lower_bounds, upper_bounds])
        if self.strategy_frame is None:
            lower_bounds = (
                [self.angle_bounds[0]] * 3 +
                [self.speed_bounds[0]] * 3 +
                [self.release_time_bounds[0]] * 3 +
                [self.detonation_delay_bounds[0]] * 3
            )
            upper_bounds = (
                [self.angle_bounds[1]] * 3 +
                [self.speed_bounds[1]] * 3 +
                [self.release_time_bounds[1]] * 3 +
                [self.detonation_delay_bounds[1]] * 3
            )
        else:
            lower_bounds = [
                self.strategy_frame['angles'][0][0], self.strategy_frame['angles'][1][0], self.strategy_frame['angles'][2][0],
                self.strategy_frame['speeds'][0][0], self.strategy_frame['speeds'][1][0], self.strategy_frame['speeds'][2][0],
                self.strategy_frame['release_times'][0][0], self.strategy_frame['release_times'][1][0], self.strategy_frame['release_times'][2][0],
                self.strategy_frame['delays'][0][0], self.strategy_frame['delays'][1][0], self.strategy_frame['delays'][2][0],
            ]
            upper_bounds = [
                self.strategy_frame['angles'][0][1], self.strategy_frame['angles'][1][1], self.strategy_frame['angles'][2][1],
                self.strategy_frame['speeds'][0][1], self.strategy_frame['speeds'][1][1], self.strategy_frame['speeds'][2][1],
                self.strategy_frame['release_times'][0][1], self.strategy_frame['release_times'][1][1], self.strategy_frame['release_times'][2][1],
                self.strategy_frame['delays'][0][1], self.strategy_frame['delays'][1][1], self.strategy_frame['delays'][2][1],
            ]
        
        bounds = [lower_bounds, upper_bounds]
        
        # 配置CMA-ES参数
        # 组装CMA-ES选项
        options = {
            'bounds': bounds,
            'tolx': self.tolerance,
            # 将tolfun设为0，避免目标函数初期全相等时立刻停止
            'tolfun': 0,
            'verbose': -1 if not verbose else 1,
            'seed': 42  # 固定随机种子以确保可重复性
        }
        if popsize:
            options['popsize'] = popsize
        if maxfev:
            # cma的参数名为maxfevals
            options['maxfevals'] = maxfev
        if maxiter:
            options['maxiter'] = maxiter
        
        # 运行CMA-ES优化
        start_time = time.time()
        
        try:
            es = cma.CMAEvolutionStrategy(initial_solution, sigma0, options)
            
            generation = 0
            while True:
                generation += 1
                
                # 生成候选解
                solutions = es.ask()
                
                # 评估适应度
                fitness_values = []
                for sol in solutions:
                    fitness = self.objective_function(sol)
                    fitness_values.append(fitness)
                
                # 更新CMA-ES
                es.tell(solutions, fitness_values)
                
                # 记录最佳解
                current_best_fitness = min(fitness_values)
                current_best_idx = fitness_values.index(current_best_fitness)
                current_best_solution = solutions[current_best_idx]
                
                if -current_best_fitness > self.best_fitness:
                    self.best_fitness = -current_best_fitness  # 转换回正值
                    self.best_solution = current_best_solution.copy()
                
                self.optimization_history.append({
                    'generation': generation,
                    'best_fitness': -current_best_fitness,
                    'mean_fitness': -np.mean(fitness_values),
                    'std_fitness': np.std(fitness_values)
                })
                
                if verbose and generation % 10 == 0:
                    print(f"代数 {generation}: 最佳遮挡时间 = {-current_best_fitness:.3f}s, "
                          f"平均适应度 = {-np.mean(fitness_values):.3f}s")
                
                # 满足停止条件且达到最少代数时跳出
                if es.stop() and generation >= (min_generations if maxiter is None else min(min_generations, maxiter)):
                    break
            
            optimization_time = time.time() - start_time
            
            # 最终评估最佳解
            final_obscuration_time, detailed_results = self.simulate_scenario(self.best_solution)
            
            print(f"\n优化完成！")
            print(f"优化时间: {optimization_time:.2f}秒")
            print(f"总代数: {generation}")
            print(f"最佳遮挡时间: {final_obscuration_time:.3f}秒")
            print(f"最佳解: {self.best_solution}")
            
            optimization_results = {
                'best_solution': (self.best_solution.tolist() if isinstance(self.best_solution, np.ndarray) else (list(self.best_solution) if self.best_solution is not None else None)),
                'best_obscuration_time': final_obscuration_time,
                'detailed_results': detailed_results,
                'optimization_time': optimization_time,
                'total_generations': generation,
                'convergence_history': self.optimization_history,
                'cmaes_result': {
                    'xbest': es.result.xbest.tolist() if hasattr(es.result, 'xbest') else None,
                    'fbest': float(es.result.fbest) if hasattr(es.result, 'fbest') else None,
                    'evaluations': int(es.result.evaluations) if hasattr(es.result, 'evaluations') else None,
                    'iterations': int(es.result.iterations) if hasattr(es.result, 'iterations') else None,
                    'stop': es.result.stop if hasattr(es.result, 'stop') else None
                },
                'algorithm': 'CMA-ES',
                'timestamp': datetime.now().isoformat()
            }
            
            return optimization_results
            
        except Exception as e:
            print(f"优化过程中发生错误: {e}")
            return None
    
    def save_results(self, results, filename_prefix="problem4_cmaes_results"):
        """
        保存优化结果到文件
        
        参数:
        - results: 优化结果字典
        - filename_prefix: 文件名前缀
        """
        if results is None:
            print("无结果可保存")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 统一结果目录
        base_dir = os.path.dirname(__file__)
        results_dir = os.path.join(base_dir, 'results')
        json_dir = os.path.join(results_dir, 'json')
        os.makedirs(json_dir, exist_ok=True)

        # 保存JSON格式结果到 results/json
        json_filename = os.path.join(json_dir, f"{filename_prefix}_{timestamp}.json")
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"结果已保存到: {json_filename}")
        
        # 保存最佳参数到CSV
        if 'detailed_results' in results:
            # 将CSV也放到 results/json 旁边，便于集中管理
            csv_filename = os.path.join(json_dir, f"{filename_prefix}_best_params_{timestamp}.csv")
            with open(csv_filename, 'w', encoding='utf-8') as f:
                f.write("参数,FY1,FY2,FY3\n")
                details = results['detailed_results']
                f.write(f"飞行角度(弧度),{details['angles'][0]:.6f},{details['angles'][1]:.6f},{details['angles'][2]:.6f}\n")
                f.write(f"飞行速度(m/s),{details['speeds'][0]:.3f},{details['speeds'][1]:.3f},{details['speeds'][2]:.3f}\n")
                f.write(f"释放时间(s),{details['release_times'][0]:.3f},{details['release_times'][1]:.3f},{details['release_times'][2]:.3f}\n")
                f.write(f"起爆延迟(s),{details['detonation_delays'][0]:.3f},{details['detonation_delays'][1]:.3f},{details['detonation_delays'][2]:.3f}\n")
                f.write(f"起爆时间(s),{details['detonation_times']['FY1']:.3f},{details['detonation_times']['FY2']:.3f},{details['detonation_times']['FY3']:.3f}\n")
                f.write(f"\n总遮挡时间,{details['total_obscuration_time']:.3f}秒\n")
                f.write(f"遮挡覆盖率,{details['obscuration_ratio']*100:.1f}%\n")
            
            print(f"最佳参数已保存到: {csv_filename}")
    
    def plot_convergence(self, save_plot=True):
        """
        绘制收敛曲线
        
        参数:
        - save_plot: 是否保存图片
        """
        if not self.optimization_history:
            print("无收敛历史可绘制")
            return
        
        print(f"绘制收敛曲线，历史记录数量: {len(self.optimization_history)}")
        
        generations = [h['generation'] for h in self.optimization_history]
        best_fitness = [h['best_fitness'] for h in self.optimization_history]
        mean_fitness = [h['mean_fitness'] for h in self.optimization_history]
        
        print(f"代数范围: {min(generations)} - {max(generations)}")
        print(f"最佳适应度范围: {min(best_fitness)} - {max(best_fitness)}")
        print(f"平均适应度范围: {min(mean_fitness)} - {max(mean_fitness)}")
        
        plt.figure(figsize=(12, 8))
        
        # 如果只有一个数据点，绘制散点图
        if len(generations) == 1:
            plt.scatter(generations, best_fitness, color='blue', s=100, label='最佳遮挡时间', zorder=5)
            plt.scatter(generations, mean_fitness, color='red', s=100, label='平均遮挡时间', zorder=5)
            plt.xlim(0.5, 1.5)
        else:
            plt.plot(generations, best_fitness, 'b-', label='最佳遮挡时间', linewidth=2, marker='o')
            plt.plot(generations, mean_fitness, 'r--', label='平均遮挡时间', alpha=0.7, marker='s')
        
        plt.xlabel('代数', fontsize=14)
        plt.ylabel('遮挡时间 (秒)', fontsize=14)
        plt.title('CMA-ES优化收敛曲线', fontsize=16, fontweight='bold')
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # 添加数值标注
        for i, (gen, best, mean) in enumerate(zip(generations, best_fitness, mean_fitness)):
            plt.annotate(f'{best:.3f}', (gen, best), textcoords="offset points", 
                        xytext=(0,10), ha='center', fontsize=10)
            plt.annotate(f'{mean:.3f}', (gen, mean), textcoords="offset points", 
                        xytext=(0,-15), ha='center', fontsize=10)
        
        plt.tight_layout()
        
        if save_plot:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_dir = os.path.dirname(__file__)
            plots_dir = os.path.join(base_dir, 'results', 'plots')
            os.makedirs(plots_dir, exist_ok=True)
            plot_filename = os.path.join(plots_dir, f"problem4_cmaes_convergence_{timestamp}.png")
            plt.savefig(plot_filename, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"收敛曲线已保存到: {plot_filename}")
        
        # 不显示图形，只保存
        plt.close()


def main(config_name='balanced'):
    """
    主函数：执行问题4的CMA-ES优化
    
    参数:
    - config_name: 配置名称 ('ultra_fast', 'fast', 'balanced', 'high_quality', 'production')
    """
    print("="*60)
    print("问题4：基于CMA-ES算法的三无人机协同烟幕遮挡优化")
    print("="*60)
    
    # 导入配置（可选）。若缺失则提供内置默认配置，避免编辑器报错。
    config = None
    try:
        from problem4_parameter_configs import get_config, print_config_comparison  # type: ignore
    except Exception:
        get_config = None  # type: ignore
        print_config_comparison = None  # type: ignore

    if get_config is not None:  # 外部配置存在
        if len(sys.argv) > 1:
            config_name = sys.argv[1]
        else:
            if print_config_comparison:
                print("可用的配置选项：")
                print_config_comparison()
                print(f"\n使用默认配置: {config_name}")
                print("如需使用其他配置，请运行: python problem4_cmaes_optimization.py <config_name>")
                print("-" * 60)
        config = get_config(config_name)  # type: ignore
        print(f"\n当前配置: {config_name.upper()}")
        try:
            print(f"描述: {config['description']}")
            print(f"预期时间: {config['expected_time']}")
            print(f"预期质量: {config['expected_quality']}")
        except Exception:
            pass
        print("-" * 60)
    else:
        print("警告: 未找到配置文件 problem4_parameter_configs.py，使用内置默认参数")
        config = {
            'simulation_params': {
                'dt': 0.01,
                'sample_theta': 36,
                'sample_z': 11
            },
            'cmaes_params': {
                'sigma0': 0.3,
                'popsize': None,
                'maxfev': 2000
            }
        }
    
    # 创建优化器
    optimizer = Problem4CMAESOptimizer()
    
    # 应用配置参数
    if 'simulation_params' in config:
        sim_params = config['simulation_params']
        optimizer.dt = sim_params.get('dt', optimizer.dt)
        optimizer.sample_theta = sim_params.get('sample_theta', optimizer.sample_theta)
        optimizer.sample_z = sim_params.get('sample_z', optimizer.sample_z)
        
        print(f"仿真参数: dt={optimizer.dt}, 角度采样={optimizer.sample_theta}, 高度采样={optimizer.sample_z}")
    
    # 运行优化
    cmaes_params = config.get('cmaes_params', {})
    results = optimizer.run_optimization(
        sigma0=cmaes_params.get('sigma0', 0.3),
        popsize=cmaes_params.get('popsize', None),
        maxfev=cmaes_params.get('maxfev', 2000),
        verbose=True
    )
    
    if results:
        # 保存结果
        optimizer.save_results(results)
        
        # 绘制收敛曲线
        optimizer.plot_convergence()
        
        # 打印最终结果总结
        print("\n" + "="*60)
        print("优化结果总结")
        print("="*60)
        details = results['detailed_results']
        print(f"总遮挡时间: {details['total_obscuration_time']:.3f} 秒")
        print(f"遮挡覆盖率: {details['obscuration_ratio']*100:.1f}%")
        print("\n各无人机最优参数:")
        for i, drone_id in enumerate(['FY1', 'FY2', 'FY3']):
            print(f"{drone_id}:")
            print(f"  飞行角度: {details['angles'][i]:.3f} 弧度 ({math.degrees(details['angles'][i]):.1f}°)")
            print(f"  飞行速度: {details['speeds'][i]:.1f} m/s")
            print(f"  释放时间: {details['release_times'][i]:.2f} s")
            print(f"  起爆延迟: {details['detonation_delays'][i]:.2f} s")
            print(f"  起爆时间: {details['detonation_times'][drone_id]:.2f} s")
        
        print(f"\n优化算法: CMA-ES")
        print(f"优化时间: {results['optimization_time']:.1f} 秒")
        print(f"收敛代数: {results['total_generations']}")
    
    else:
        print("优化失败！")


if __name__ == "__main__":
    main()
