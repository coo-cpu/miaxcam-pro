import pandas as pd
import numpy as np
import io

# --- 1. 内置数据 ---
# 我已将 "RL分压法" 的数据块从 CSV 复制到这里
# (l(mm),Vi(Vpp),VR(Vpp))
# "..." 代表无效数据，我们将在后面清理掉
data_block = """
l(mm),Vi(Vpp),VR(Vpp)
-50,...
-45,4.88,1.76
-40,4.88,1.73
-35,4.88,1.72
-30,4.88,1.68
-25,4.88,1.67
-20,4.88,1.66
-15,4.88,1.64
-10,4.88,1.64
-5,4.88,1.62
0,4.88,1.62
5,4.88,1.62
10,4.88,1.64
15,4.88,1.64
20,4.88,1.64
25,4.88,1.64
30,4.88,1.64
35,4.88,1.66
40,4.88,1.68
45,4.88,1.7
50,4.88,1.7
55,4.88,1.73
60,4.88,1.76
65,4.88,1.82
70,4.8,1.86
75,4.72,1.88
80,4.72,1.96
85,4.72,2.04
90,4.64,2.14
"""

# --- 2. 定义常量 (根据您的指令) ---
R = 100.0       # 欧姆 (Ohm)
f = 10000.0     # 赫兹 (Hz) (您指定 10kHz)
omega = 2 * np.pi * f # 角频率

print("--- 正在处理内置的 'RL分压法' 数据 ---")

try:
    # --- 3. 加载数据 ---
    # 使用 io.StringIO 将字符串模拟为文件
    # header=0 表示第一行 "l(mm),Vi(Vpp),VR(Vpp)" 是表头
    df = pd.read_csv(io.StringIO(data_block), header=0)
    
    # 重命名列以方便使用 (虽然已经匹配，但保留好习惯)
    df.columns = ['dx_mm', 'Vi_vpp', 'VR_vpp']
    
    # --- 4. 打印原始数据 (供您审核) ---
    print("\n--- 步骤 1: 原始数据审核 ---")
    print("请您检查以下数据是否与 'RL分压法' 一致：")
    print(df.to_string()) # to_string() 打印完整的 DataFrame

    # --- 5. 清理数据 ---
    # 将 '...' 或其他非数值转为 NaN
    df_cleaned = df.apply(pd.to_numeric, errors='coerce')
    
    # 删除包含 NaN 的行 (比如 -50 那一行)
    df_cleaned = df_cleaned.dropna()
    
    print("\n--- 步骤 2: 清理后的数据 (已移除无效行) ---")
    print(df_cleaned.to_string())

    # --- 6. 计算电感 L (根据您提供的公式) ---
    # 公式: L = (R / omega) * sqrt((Vi / VR)^2 - 1)
    
    # 计算 (Vi / VR)^2
    vi_vr_ratio_sq = (df_cleaned['Vi_vpp'] / df_cleaned['VR_vpp'])**2
    
    # 确保根号内的值 >= 0 (处理 V_R > V_i 的异常情况或测量误差)
    vi_vr_ratio_sq[vi_vr_ratio_sq < 1] = 1.0
    
    # 计算 L (单位: 亨 H)
    df_cleaned['L_Henry'] = (R / omega) * np.sqrt(vi_vr_ratio_sq - 1)
    
    # 转换 L (单位: 毫亨 mH)
    df_cleaned['L_mH'] = df_cleaned['L_Henry'] * 1000
    
    # --- 7. 打印计算结果 ---
    print("\n--- 步骤 3: 电感 L 计算结果 (f=10kHz) ---")
    # 只显示位移和计算出的电感
    print(df_cleaned[['dx_mm', 'L_mH']].to_string())

except Exception as e:
    print(f"处理数据时出错: {e}")