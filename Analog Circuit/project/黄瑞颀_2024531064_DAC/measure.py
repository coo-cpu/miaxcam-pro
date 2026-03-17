import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io

# 模拟读取 CSV 数据
csv_data = """Digital Input（B）,Vtheory（V）,Vmeasure(V),DNL,INL
000,0.9,0.902,,0.0267687448135557
001,0.975,1.004,0.36,0.388146799796558
010,1.05,1.067,-0.160000000000001,0.227534330915222
011,1.125,1.129,-0.173333333333333,0.0535374896271114
100,1.2,1.204,0,0.0535374896271114
101,1.275,1.302,0.306666666666668,0.361378054983004
110,1.35,1.366,-0.146666666666666,0.214149958508446
111,1.425,1.425,-0.213333333333334,0"""

df = pd.read_csv(io.StringIO(csv_data))

# 提取数据
digital_codes = df['Digital Input（B）']
v_theory = df['Vtheory（V）']
v_measure = df['Vmeasure(V)']

# 创建 Y 轴的数值索引 (0, 1, ..., 7) 对应二进制码
y_indices = np.arange(len(digital_codes))

# 设置绘图风格
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(10, 6))

# --- 绘制内容 ---
# 1. 绘制理想线 (Theory) - 灰色虚线
ax.step(v_theory, y_indices, where='post', label='Ideal ADC (Theory)', 
        color='gray', linestyle='--', linewidth=2, alpha=0.7)

# 2. 绘制实测线 (Measure) - 蓝色实线带点
ax.step(v_measure, y_indices, where='post', label='Actual ADC (Measured)', 
        color='blue', linewidth=2, marker='o', markersize=6)

# --- 图表美化 ---

ax.set_title('DAC Transfer Characteristic', fontsize=14, fontweight='bold', pad=15)

# X 轴设置：使用简单的 0-7 索引
# 我们需要先找到这 8 个点的“位置”。既然您不想显示具体的电压值，
# 我们可以在 X 轴上，在每个实测电压点的位置，标上对应的序号 0-7。
ax.set_xlabel('Measurement Points (0-7)', fontsize=12)

# 设置 X 轴刻度为实测电压的位置
ax.set_xticks(v_measure)
# 将刻度标签强制设置为 0 到 7
ax.set_xticklabels(range(8), fontsize=10)

# 设置 X 轴范围，稍微留白
ax.set_xlim(0.85, 1.45)

# Y 轴设置：二进制代码
ax.set_ylabel('Digital Input Code', fontsize=12)
ax.set_yticks(y_indices)
ax.set_yticklabels(digital_codes, fontsize=10)
ax.set_ylim(-0.5, 7.5)

# 网格
ax.grid(True, linestyle='--', alpha=0.6)

# 图例
ax.legend(loc='lower right', frameon=True, framealpha=0.9, shadow=True)

# 保存
plt.tight_layout()
plt.savefig('dac_transfer_curve.png', dpi=300)
print("图表已生成: dac_transfer_curve.png")

plt.show()



# 模拟读取 CSV 数据
csv_data = """Digital Input（B）,Vtheory（V）,Vmeasure(V),DNL,INL
000,0.9,0.902,,0.0267687448135557
001,0.975,1.004,0.36,0.388146799796558
010,1.05,1.067,-0.160000000000001,0.227534330915222
011,1.125,1.129,-0.173333333333333,0.0535374896271114
100,1.2,1.204,0,0.0535374896271114
101,1.275,1.302,0.306666666666668,0.361378054983004
110,1.35,1.366,-0.146666666666666,0.214149958508446
111,1.425,1.425,-0.213333333333334,0"""

df = pd.read_csv(io.StringIO(csv_data))

# 提取数据
digital_codes = df['Digital Input（B）']
v_theory = df['Vtheory（V）']
v_measure = df['Vmeasure(V)']
# 填充空值以便绘图（例如起点可能没有 DNL）
dnl_data = df['DNL'].fillna(0)
inl_data = df['INL'].fillna(0)

# 创建 Y 轴的数值索引 (0, 1, ..., 7) 对应二进制码
y_indices = np.arange(len(digital_codes))

# 设置绘图风格
plt.style.use('seaborn-v0_8-whitegrid')

# --- 图表 1: 传输特性曲线 (Transfer Curve) ---
fig1, ax1 = plt.subplots(figsize=(10, 6))

# 1. 绘制理想线 (Theory) - 灰色虚线
ax1.step(v_theory, y_indices, where='post', label='Ideal ADC (Theory)', 
        color='gray', linestyle='--', linewidth=2, alpha=0.7)

# 2. 绘制实测线 (Measure) - 蓝色实线带点
ax1.step(v_measure, y_indices, where='post', label='Actual ADC (Measured)', 
        color='blue', linewidth=2, marker='o', markersize=6)

ax1.set_title('DAC Transfer Characteristic', fontsize=14, fontweight='bold', pad=15)
ax1.set_xlabel('Measurement Points (0-7)', fontsize=12)
ax1.set_xticks(v_measure)
ax1.set_xticklabels(range(8), fontsize=10)
ax1.set_xlim(0.85, 1.45)
ax1.set_ylabel('Digital Input Code', fontsize=12)
ax1.set_yticks(y_indices)
ax1.set_yticklabels(digital_codes, fontsize=10)
ax1.set_ylim(-0.5, 7.5)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(loc='lower right', frameon=True, framealpha=0.9, shadow=True)
plt.tight_layout()
plt.savefig('dac_transfer_curve.png', dpi=300)
print("图表已生成: dac_transfer_curve.png")


# --- 图表 2: DNL 柱状图 ---
fig2, ax2 = plt.subplots(figsize=(10, 5))

# 创建柱状图
bars_dnl = ax2.bar(y_indices, dnl_data, color='teal', alpha=0.7, width=0.6, edgecolor='black')

# 美化
ax2.set_title('Differential Nonlinearity (DNL)', fontsize=14, fontweight='bold', pad=15)
ax2.set_xlabel('Digital Input Code', fontsize=12)
ax2.set_ylabel('DNL (LSB)', fontsize=12)

# 设置 X 轴为二进制码
ax2.set_xticks(y_indices)
ax2.set_xticklabels(digital_codes, fontsize=10)

# 添加参考线 (0 LSB, +0.5 LSB, -0.5 LSB)
ax2.axhline(0, color='black', linewidth=1)
ax2.axhline(0.5, color='red', linestyle='--', linewidth=1, label='Limit (+0.5 LSB)')
ax2.axhline(-0.5, color='red', linestyle='--', linewidth=1, label='Limit (-0.5 LSB)')

# 在柱子上标注数值
for bar in bars_dnl:
    height = bar.get_height()
    if height != 0:
        ax2.text(bar.get_x() + bar.get_width()/2., height + (0.02 if height > 0 else -0.04),
                f'{height:.2f}', ha='center', va='bottom' if height > 0 else 'top', fontsize=9)

ax2.set_ylim(min(dnl_data.min(), -0.6) - 0.1, max(dnl_data.max(), 0.6) + 0.1)
ax2.legend(loc='upper right')
ax2.grid(True, axis='y', linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig('dac_dnl_chart.png', dpi=300)
print("图表已生成: dac_dnl_chart.png")


# --- 图表 3: INL 柱状图 ---
fig3, ax3 = plt.subplots(figsize=(10, 5))

# 创建柱状图
bars_inl = ax3.bar(y_indices, inl_data, color='purple', alpha=0.7, width=0.6, edgecolor='black')

# 美化
ax3.set_title('Integral Nonlinearity (INL)', fontsize=14, fontweight='bold', pad=15)
ax3.set_xlabel('Digital Input Code', fontsize=12)
ax3.set_ylabel('INL (LSB)', fontsize=12)

# 设置 X 轴为二进制码
ax3.set_xticks(y_indices)
ax3.set_xticklabels(digital_codes, fontsize=10)

# 添加参考线 (0 LSB, +1.0 LSB, -1.0 LSB)
ax3.axhline(0, color='black', linewidth=1)
ax3.axhline(1.0, color='red', linestyle='--', linewidth=1, label='Limit (+1.0 LSB)')
ax3.axhline(-1.0, color='red', linestyle='--', linewidth=1, label='Limit (-1.0 LSB)')

# 在柱子上标注数值
for bar in bars_inl:
    height = bar.get_height()
    if height != 0:
        ax3.text(bar.get_x() + bar.get_width()/2., height + (0.02 if height > 0 else -0.04),
                f'{height:.2f}', ha='center', va='bottom' if height > 0 else 'top', fontsize=9)

ax3.set_ylim(min(inl_data.min(), -1.1) - 0.1, max(inl_data.max(), 1.1) + 0.1)
ax3.legend(loc='upper right')
ax3.grid(True, axis='y', linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig('dac_inl_chart.png', dpi=300)
print("图表已生成: dac_inl_chart.png")

plt.show()

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io

# 模拟读取 CSV 数据
csv_data = """Digital Input（B）,Vtheory（V）,Vmeasure(V),DNL,INL
000,0.9,0.902,,0.0267687448135557
001,0.975,1.004,0.36,0.388146799796558
010,1.05,1.067,-0.160000000000001,0.227534330915222
011,1.125,1.129,-0.173333333333333,0.0535374896271114
100,1.2,1.204,0,0.0535374896271114
101,1.275,1.302,0.306666666666668,0.361378054983004
110,1.35,1.366,-0.146666666666666,0.214149958508446
111,1.425,1.425,-0.213333333333334,0"""

df = pd.read_csv(io.StringIO(csv_data))

# 提取数据
digital_codes = df['Digital Input（B）']
v_theory = df['Vtheory（V）']
v_measure = df['Vmeasure(V)']
# 填充空值以便绘图（例如起点可能没有 DNL）
dnl_data = df['DNL'].fillna(0)
inl_data = df['INL'].fillna(0)

# 创建 Y 轴的数值索引 (0, 1, ..., 7) 对应二进制码
y_indices = np.arange(len(digital_codes))

# 设置绘图风格
plt.style.use('seaborn-v0_8-whitegrid')

# --- 图表 1: 传输特性曲线 (Transfer Curve) ---
fig1, ax1 = plt.subplots(figsize=(10, 6))

# 1. 绘制理想线 (Theory) - 灰色虚线
ax1.step(v_theory, y_indices, where='post', label='Ideal ADC (Theory)', 
        color='gray', linestyle='--', linewidth=2, alpha=0.7)

# 2. 绘制实测线 (Measure) - 蓝色实线带点
ax1.step(v_measure, y_indices, where='post', label='Actual ADC (Measured)', 
        color='blue', linewidth=2, marker='o', markersize=6)

ax1.set_title('DAC Transfer Characteristic', fontsize=14, fontweight='bold', pad=15)
ax1.set_xlabel('Measurement Points (0-7)', fontsize=12)
ax1.set_xticks(v_measure)
ax1.set_xticklabels(range(8), fontsize=10)
ax1.set_xlim(0.85, 1.45)
ax1.set_ylabel('Digital Input Code', fontsize=12)
ax1.set_yticks(y_indices)
ax1.set_yticklabels(digital_codes, fontsize=10)
ax1.set_ylim(-0.5, 7.5)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(loc='lower right', frameon=True, framealpha=0.9, shadow=True)
plt.tight_layout()
plt.savefig('dac_transfer_curve.png', dpi=300)
print("图表已生成: dac_transfer_curve.png")


# --- 图表 2: DNL 柱状图 ---
fig2, ax2 = plt.subplots(figsize=(10, 5))

# 创建柱状图
bars_dnl = ax2.bar(y_indices, dnl_data, color='teal', alpha=0.7, width=0.6, edgecolor='black')

# 美化
ax2.set_title('Differential Nonlinearity (DNL)', fontsize=14, fontweight='bold', pad=15)
ax2.set_xlabel('Digital Input Code', fontsize=12)
ax2.set_ylabel('DNL (LSB)', fontsize=12)

# 设置 X 轴为二进制码
ax2.set_xticks(y_indices)
ax2.set_xticklabels(digital_codes, fontsize=10)

# 添加参考线 (0 LSB, +0.5 LSB, -0.5 LSB)
ax2.axhline(0, color='black', linewidth=1)
ax2.axhline(0.5, color='red', linestyle='--', linewidth=1, label='Limit (+0.5 LSB)')
ax2.axhline(-0.5, color='red', linestyle='--', linewidth=1, label='Limit (-0.5 LSB)')

# 在柱子上标注数值
for bar in bars_dnl:
    height = bar.get_height()
    if height != 0:
        ax2.text(bar.get_x() + bar.get_width()/2., height + (0.02 if height > 0 else -0.04),
                f'{height:.2f}', ha='center', va='bottom' if height > 0 else 'top', fontsize=9)

ax2.set_ylim(min(dnl_data.min(), -0.6) - 0.1, max(dnl_data.max(), 0.6) + 0.1)
ax2.legend(loc='upper right')
ax2.grid(True, axis='y', linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig('dac_dnl_chart.png', dpi=300)
print("图表已生成: dac_dnl_chart.png")


# --- 图表 3: INL 柱状图 ---
fig3, ax3 = plt.subplots(figsize=(10, 5))

# 创建柱状图
bars_inl = ax3.bar(y_indices, inl_data, color='purple', alpha=0.7, width=0.6, edgecolor='black')

# 美化
ax3.set_title('Integral Nonlinearity (INL)', fontsize=14, fontweight='bold', pad=15)
ax3.set_xlabel('Digital Input Code', fontsize=12)
ax3.set_ylabel('INL (LSB)', fontsize=12)

# 设置 X 轴为二进制码
ax3.set_xticks(y_indices)
ax3.set_xticklabels(digital_codes, fontsize=10)

# 添加参考线 (0 LSB, +1.0 LSB, -1.0 LSB)
ax3.axhline(0, color='black', linewidth=1)
ax3.axhline(1.0, color='red', linestyle='--', linewidth=1, label='Limit (+1.0 LSB)')
ax3.axhline(-1.0, color='red', linestyle='--', linewidth=1, label='Limit (-1.0 LSB)')

# 在柱子上标注数值
for bar in bars_inl:
    height = bar.get_height()
    if height != 0:
        ax3.text(bar.get_x() + bar.get_width()/2., height + (0.02 if height > 0 else -0.04),
                f'{height:.2f}', ha='center', va='bottom' if height > 0 else 'top', fontsize=9)

ax3.set_ylim(min(inl_data.min(), -1.1) - 0.1, max(inl_data.max(), 1.1) + 0.1)
ax3.legend(loc='upper right')
ax3.grid(True, axis='y', linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig('dac_inl_chart.png', dpi=300)
print("图表已生成: dac_inl_chart.png")


# --- 图表 4: 线性对比图 (Line Chart) ---
fig4, ax4 = plt.subplots(figsize=(10, 6))

# 这张图的 X 轴通常是 Input Code (0-7)，Y 轴是 Output Voltage
# 这样更符合 "输入变化引起输出变化" 的直观感受，且能连成线

# 1. 绘制理想线 (Theory) - 灰色虚线
# 使用普通的 plot (不是 step)，连接所有点
ax4.plot(y_indices, v_theory, label='Ideal ADC (Theory)', 
        color='gray', linestyle='--', linewidth=2, marker='s', markersize=4, alpha=0.7)

# 2. 绘制实测线 (Measure) - 蓝色实线带点
ax4.plot(y_indices, v_measure, label='Actual ADC (Measured)', 
        color='blue', linewidth=2, marker='o', markersize=6)

ax4.set_title('Vout Linearity: Theory vs Measurement', fontsize=14, fontweight='bold', pad=15)
ax4.set_xlabel('Digital Input Code', fontsize=12)
ax4.set_ylabel('Output Voltage (V)', fontsize=12)

# 设置 X 轴为二进制码
ax4.set_xticks(y_indices)
ax4.set_xticklabels(digital_codes, fontsize=10)

# 设置 Y 轴范围和网格
ax4.set_ylim(0.85, 1.45)
ax4.grid(True, linestyle='--', alpha=0.6)

# 添加数值标签 (可选)
for i, v in enumerate(v_measure):
    ax4.text(i, v + 0.015, f"{v:.3f}", ha='center', fontsize=8, color='blue')

ax4.legend(loc='upper left', frameon=True, framealpha=0.9, shadow=True)
plt.tight_layout()
plt.savefig('dac_linearity_line_chart.png', dpi=300)
print("图表已生成: dac_linearity_line_chart.png")

plt.show()