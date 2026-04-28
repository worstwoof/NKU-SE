import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. 参数设定
# ==========================================
TARGET_MASS = 100 * 10**6  
START_YEAR = 2050

# 排放系数 (假设值，相对大小是关键)
# 火箭: 黑碳 + 臭氧损耗 + 噪音 + CO2 (设为 100)
FACTOR_ROCKET = 100.0 
# 电梯: 主要是电力来源的碳足迹 (设为 1，假设使用核能/太阳能)
FACTOR_SE = 1.0       

# 基础运力参数 (沿用之前的)
SE_BASE_CAPACITY = 3 * 179000
SE_GROWTH_RATE = 0.08
ROCKET_ANNUAL_CAPACITY = 10 * 15 * (365/7) * 150

def calculate_impact(strategy):
    cumulative_mass = 0
    cumulative_impact = [0]
    years = [START_YEAR]
    t = 0
    
    current_impact_score = 0
    
    while cumulative_mass < TARGET_MASS and t < 150:
        # 1. 计算运量
        mass_se = 0
        mass_rocket = 0
        
        # 电梯运力
        if strategy != 'Rocket_Only':
            mass_se = SE_BASE_CAPACITY * ((1 + SE_GROWTH_RATE) ** t)
        
        # 火箭运力
        if strategy == 'Rocket_Only':
            mass_rocket = ROCKET_ANNUAL_CAPACITY
        elif strategy == 'Hybrid':
            if t < 10: # 混合策略前10年用火箭
                mass_rocket = ROCKET_ANNUAL_CAPACITY
        
        # 2. 计算环境影响
        # Impact = Mass * Factor
        annual_impact = (mass_rocket * FACTOR_ROCKET) + (mass_se * FACTOR_SE)
        current_impact_score += annual_impact
        
        # 更新状态
        cumulative_mass += mass_se + mass_rocket
        cumulative_impact.append(current_impact_score / 10**6) # 缩放数值
        t += 1
        years.append(START_YEAR + t)
        
    return years, cumulative_impact

# ==========================================
# 2. 运行计算
# ==========================================
res_rocket = calculate_impact('Rocket_Only')
res_se = calculate_impact('SE_Only') # 这里的 SE_Only 指含增长的
res_hybrid = calculate_impact('Hybrid')

# ==========================================
# 3. 绘图
# ==========================================
plt.figure(figsize=(10, 6))

plt.plot(res_rocket[0], res_rocket[1], label='Rockets Only (High Pollution)', color='red', linestyle='-.', linewidth=2)
plt.plot(res_hybrid[0], res_hybrid[1], label='Hybrid Strategy (Balanced)', color='green', linewidth=3)
plt.plot(res_se[0], res_se[1], label='Space Elevator Only (Green)', color='blue', linestyle='--', linewidth=2)

plt.title('Cumulative Environmental Impact Assessment', fontsize=14)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Environmental Impact Index (Arbitrary Units)', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend()

# 标注混合策略的转折点
turn_point_idx = 10
plt.scatter([res_hybrid[0][turn_point_idx]], [res_hybrid[1][turn_point_idx]], color='green', s=100, zorder=5)
plt.text(res_hybrid[0][turn_point_idx]+2, res_hybrid[1][turn_point_idx], 
         'Rocket Phase Ends\n(Impact Stabilizes)', fontsize=10, color='green', va='center')

plt.tight_layout()
plt.savefig('Task4_Environment.png')
plt.show()