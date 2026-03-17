import numpy as np
from scipy.optimize import fsolve

# --- 数据点 ---
# 数据点 1: 频率 f1 = 100 kHz, 增益 A1 = 4000
f1 = 1e5  # 100 kHz in Hz
A1 = 4e3

# 数据点 2: 频率 f2 = 1 MHz, 增益 A2 = 800
f2 = 1e6  # 1 MHz in Hz
A2 = 800

# 定义需要求解的方程组
# unknowns 是一个包含两个未知数的列表: unknowns[0] = A0, unknowns[1] = fb
def equations(unknowns):
    A0, fb = unknowns
    # 根据讲义第11页的公式 |A(f)| = A0 / sqrt(1 + (f/fb)^2)
    # 我们将方程变形为 F(x) = 0 的形式
    
    # 方程 1: A0 / sqrt(1 + (f1/fb)^2) - A1 = 0
    eq1 = A0 / np.sqrt(1 + (f1 / fb)**2) - A1
    
    # 方程 2: A0 / sqrt(1 + (f2/fb)^2) - A2 = 0
    eq2 = A0 / np.sqrt(1 + (f2 / fb)**2) - A2
    
    return [eq1, eq2]

# --- 求解方程 ---
# 提供一个初始猜测值 [A0_guess, fb_guess]
# 根据手动估算，A0 约为 4600, fb 约为 177k
initial_guess = [4600, 177000]

# 使用 fsolve 数值求解器
solution = fsolve(equations, initial_guess)

# --- 提取并打印结果 ---
A0_solved = solution[0]
fb_solved = solution[1]
ft_solved = A0_solved * fb_solved # 单位增益频率 ft = A0 * fb

print("--- Exercise 2 参数计算结果 ---")
print(f"求解得到的直流增益 (A0): {A0_solved:.3f} V/V")
print(f"求解得到的 3-dB 频率 (fb): {fb_solved / 1e3:.3f} kHz")
print(f"计算得到的单位增益频率 (ft): {ft_solved / 1e6:.3f} MHz")
