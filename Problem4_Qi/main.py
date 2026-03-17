#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一入口 main.py
- single: 直接用 CMA-ES 跑一次单次优化（默认配置）
- hier:   运行分层（先双机/单机，再协调）策略

示例：
python main.py single
python main.py hier
"""

import sys
from pathlib import Path
import time

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from problem4_cmaes_optimization import Problem4CMAESOptimizer
from hierarchical_drone_optimizer import HierarchicalDroneOptimizer


def run_single():
    print("🚀 运行单次 CMA-ES 优化（默认配置）")
    opt = Problem4CMAESOptimizer()
    # 收紧搜索空间，加快收敛
    try:
        opt.apply_strategy_framing(mode='three_role', angle_half_width_deg=18.0)
        print("已启用策略框: three_role, ±18°")
    except Exception:
        pass
    t0 = time.time()
    # 兼容当前 API：run_optimization 返回结果字典，而非 (params, fitness) 元组
    # 轻量快速跑一轮，便于在会话内看到完整结果
    results = opt.run_optimization(popsize=16, maxfev=240, maxiter=12, verbose=True)
    dt = time.time() - t0
    if results:
        best_fitness = results.get('best_obscuration_time', None)
        print(f"✅ 完成: 最佳遮挡 {best_fitness:.3f}s，用时 {dt:.1f}s")
        details = results.get('detailed_results', {})
        if details:
            print("参数:")
            for i, d in enumerate(['FY1','FY2','FY3']):
                try:
                    print(f"  {d}: angle={details['angles'][i]:.3f}, speed={details['speeds'][i]:.1f}, release={details['release_times'][i]:.2f}, delay={details['detonation_delays'][i]:.2f}")
                except Exception:
                    break
    else:
        print("❌ 优化失败")


def run_hier():
    print("🤝 运行分层协同优化")
    h = HierarchicalDroneOptimizer()
    h.run_hierarchical_optimization()


def main():
    if len(sys.argv) < 2:
        print("用法: python main.py [single|hier]")
        return
    mode = sys.argv[1].lower()
    if mode == 'single':
        run_single()
    elif mode == 'hier':
        run_hier()
    else:
        print("未知模式，支持: single, hier")


if __name__ == '__main__':
    main()
