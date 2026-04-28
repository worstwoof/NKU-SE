import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. 参数设定
# ==========================================
# 需求参数
POPULATION = 100000
DAILY_USE = 0.05  # 吨/人/天
TOTAL_DAYS = 365
W_GROSS = POPULATION * DAILY_USE * TOTAL_DAYS # 1,825,000 吨

# 成本参数 (假设值，用于定性分析)
PRICE_TRANS = 0.2 * 10**6  # 物流单价: $0.2M/ton (太空电梯)
BETA = 2.0 * 10**9         # 技术系数 beta: 假设 20 亿美元量级

# ==========================================
# 2. 计算模型
# ==========================================
R = np.linspace(0.80, 0.995, 100) # 循环率从 80% 到 99.5%

# 物流成本: W * (1-R) * Price
cost_logistics = W_GROSS * (1 - R) * PRICE_TRANS

# 技术成本: Beta * R / (1-R)
cost_tech = BETA * (R / (1 - R))

# 总成本
cost_total = cost_logistics + cost_tech

# 找到最低点 (Optimal Point)
min_idx = np.argmin(cost_total)
opt_R = R[min_idx]
min_cost = cost_total[min_idx]

# ==========================================
# 3. 绘图
# ==========================================
plt.figure(figsize=(10, 6))

# 绘制三条线
plt.plot(R*100, cost_logistics/10**9, label='Logistics Cost (Linear)', color='blue', linestyle='--')
plt.plot(R*100, cost_tech/10**9, label='Technology Cost (Asymptotic)', color='red', linestyle='--')
plt.plot(R*100, cost_total/10**9, label='Total Cost (U-Shape)', color='black', linewidth=3)

# 标注最优点
plt.scatter([opt_R*100], [min_cost/10**9], color='green', s=100, zorder=5)
plt.axvline(opt_R*100, color='green', linestyle=':', alpha=0.8)
plt.text(opt_R*100, (min_cost/10**9) + 10, 
         f'Optimal Point\nR = {opt_R*100:.1f}%\nCost = ${min_cost/10**9:.1f}B', 
         ha='center', color='green', fontweight='bold')

plt.title('Optimization of Water Recycling Rate: Trade-off Analysis', fontsize=14)
plt.xlabel('Recycling Rate (%)', fontsize=12)
plt.ylabel('Annual Cost (Billion USD)', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend()
plt.ylim(0, 300) # 限制Y轴范围以便观察

plt.tight_layout()
plt.savefig('Task3_Optimization.png')
plt.show()

print(f"Optimal Recycling Rate: {opt_R*100:.2f}%")