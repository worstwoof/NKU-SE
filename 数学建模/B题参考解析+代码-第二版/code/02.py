import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. 参数设定 (Parameter Setup)
# ==========================================
TARGET_MASS = 100 * 10**6
SE_BASE_CAPACITY = 3 * 179000
SE_GROWTH_RATE = 0.08
ROCKET_ANNUAL_CAPACITY = 10 * 15 * (365/7) * 150
COST_SE = 0.2
COST_ROCKET = 1.5
COST_PAYLOAD = 0.5

# --- 关键修改：增加不确定性强度 ---
SIMULATION_RUNS = 2000          # 增加模拟次数让分布更平滑
ROCKET_FAIL_RATE = 0.05         # 火箭失败率提升至 5%
SE_EFFICIENCY_MEAN = 0.80       # 电梯平均效率降至 80%
SE_EFFICIENCY_STD = 0.15        # 方差增大到 15% (波动更剧烈)
SE_CATASTROPHIC_PROB = 0.02     # 2% 概率发生缆索断裂 (大灾难)

def run_monte_carlo(strategy, max_duration=150):
    cumulative_mass = 0
    total_cost = 0
    t = 0
    
    while cumulative_mass < TARGET_MASS and t < max_duration:
        # 1. 随机化电梯运力
        if strategy == 'Rocket_Only':
            mass_se = 0
        else:
            # 基础运力
            nominal_se = SE_BASE_CAPACITY * ((1 + SE_GROWTH_RATE) ** t)
            
            # --- 新增逻辑：灾难判定 ---
            if np.random.random() < SE_CATASTROPHIC_PROB:
                # 发生灾难：当年运力仅剩 10% (大维修)
                efficiency = 0.1 
            else:
                # 正常波动：正态分布
                efficiency = np.random.normal(SE_EFFICIENCY_MEAN, SE_EFFICIENCY_STD)
                efficiency = np.clip(efficiency, 0.4, 1.1) # 限制范围
            
            mass_se = nominal_se * efficiency
        
        # 2. 随机化火箭运力
        mass_rocket = 0
        cost_rocket_step = 0
        
        plan_rocket_mass = 0
        if strategy == 'Rocket_Only':
            plan_rocket_mass = ROCKET_ANNUAL_CAPACITY
        elif strategy == 'Hybrid':
            if t < 10: 
                plan_rocket_mass = ROCKET_ANNUAL_CAPACITY
        
        if plan_rocket_mass > 0:
            num_launches = int(plan_rocket_mass / 150)
            success_launches = np.random.binomial(num_launches, 1 - ROCKET_FAIL_RATE)
            fail_launches = num_launches - success_launches
            
            mass_rocket = success_launches * 150
            cost_rocket_step = (num_launches * 150 * COST_ROCKET) + \
                               (fail_launches * 150 * COST_PAYLOAD)
        
        cumulative_mass += mass_se + mass_rocket
        total_cost += (mass_se * COST_SE) + cost_rocket_step
        t += 1
        
    return t + 2050, total_cost / 10**6

# ==========================================
# 2. 执行模拟
# ==========================================
results_time = []
results_cost = []

print(f"Running {SIMULATION_RUNS} simulations (High Uncertainty)...")
for _ in range(SIMULATION_RUNS):
    y, c = run_monte_carlo('Hybrid')
    results_time.append(y)
    results_cost.append(c)

mean_time = np.mean(results_time)
mean_cost = np.mean(results_cost)

# ==========================================
# 3. 绘图 (优化版)
# ==========================================
plt.figure(figsize=(14, 6))

# 图1: 时间分布 (使用离散对齐的 bins)
plt.subplot(1, 2, 1)
# 技巧：bins 设为整数范围，让柱子对齐年份
bins_year = np.arange(min(results_time)-1, max(results_time)+2) - 0.5
plt.hist(results_time, bins=bins_year, color='#87CEFA', edgecolor='black', alpha=0.8, rwidth=0.8)
plt.axvline(mean_time, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_time:.1f} Year')
plt.title('Completion Year Distribution\n(With Catastrophic Events)', fontsize=14)
plt.xlabel('Year', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.legend()
plt.grid(axis='y', alpha=0.3)

# 图2: 成本分布
plt.subplot(1, 2, 2)
plt.hist(results_cost, bins=30, color='#90EE90', edgecolor='black', alpha=0.8)
plt.axvline(mean_cost, color='red', linestyle='--', linewidth=2, label=f'Mean: ${mean_cost:.1f}T')
plt.title('Total Cost Distribution\n(High Variance)', fontsize=14)
plt.xlabel('Cost (Trillion USD)', fontsize=12)
plt.legend()
plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('Task2_Uncertainty_Fixed.png')
plt.show()

print(f"Mean Year: {mean_time:.2f}")
print(f"Mean Cost: {mean_cost:.2f}")