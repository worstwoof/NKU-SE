import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. 参数设定 (Parameter Setup)
# ==========================================
# 目标与时间
TARGET_MASS = 100 * 10**6  # 目标: 1亿吨 (100 Million Metric Tons)
START_YEAR = 2050

# 太空电梯参数 (Space Elevator, SE)
SE_HARBOURS = 3
SE_CAPACITY_PER_HARBOUR = 179000  # 单个港湾初始运力 (吨/年)
SE_BASE_ANNUAL = SE_HARBOURS * SE_CAPACITY_PER_HARBOUR  # 总初始运力: 537,000 吨/年
SE_GROWTH_RATE = 0.08  # 技术增长因子 alpha = 8%
SE_COST_PER_TON = 0.2 * 10**6  # 成本: $200/kg = $0.2 Million/ton

# 火箭参数 (Rocket)
# 假设: 10个基地, 每个基地15个发射台, 7天周转, 150吨载重
ROCKET_SITES = 10
PADS_PER_SITE = 15
TURNAROUND_DAYS = 7
PAYLOAD = 150 # 单次载重 (吨)
# 火箭年运力计算
ROCKET_ANNUAL = ROCKET_SITES * PADS_PER_SITE * (365/TURNAROUND_DAYS) * PAYLOAD
ROCKET_COST_PER_TON = 1.5 * 10**6 # 成本: $1,500/kg = $1.5 Million/ton

# ==========================================
# 2. 模拟核心逻辑 (Simulation Logic)
# ==========================================

def simulate_scenario(scenario_type, max_years=250):
    """
    模拟不同场景下的运输过程
    :param scenario_type: 'SE_Static', 'SE_Dynamic', 'Rocket_Only', 'Hybrid'
    """
    years = []
    cumulative_mass = [0]     # 记录累计运输量
    total_cost = [0]          # 记录累计成本
    annual_capacity_log = []  # 记录当年运力
    
    current_mass = 0
    current_cost = 0
    
    for t in range(1, max_years + 1):
        year_idx = t - 1 # 0-indexed 用于指数计算
        
        # --- A. 计算当年运力 (Annual Capacity) ---
        
        # 1. 太空电梯运力 (含技术增长)
        if scenario_type == 'SE_Static':
            se_mass = SE_BASE_ANNUAL
        else:
            # 公式: Base * (1 + alpha)^t
            se_mass = SE_BASE_ANNUAL * ((1 + SE_GROWTH_RATE) ** year_idx)
            
        # 2. 火箭运力
        if scenario_type == 'Rocket_Only':
            rocket_mass = ROCKET_ANNUAL
        elif scenario_type == 'Hybrid':
            # 混合策略逻辑: 
            # 前10年(2050-2060)全速发射火箭，快速建立基础设施
            # 10年后，随着电梯运力提升，停止昂贵的火箭运输
            if t <= 10:
                rocket_mass = ROCKET_ANNUAL
            else:
                rocket_mass = 0
        else:
            rocket_mass = 0
            
        # --- B. 场景过滤 ---
        if scenario_type in ['SE_Static', 'SE_Dynamic']:
            rocket_mass = 0 # 纯电梯模式不含火箭
            
        total_annual_mass = se_mass + rocket_mass
        
        # --- C. 成本计算 ---
        annual_cost = (se_mass * SE_COST_PER_TON) + (rocket_mass * ROCKET_COST_PER_TON)
        
        # --- D. 更新状态 ---
        current_mass += total_annual_mass
        current_cost += annual_cost
        
        # 记录数据
        years.append(START_YEAR + t)
        cumulative_mass.append(current_mass / 10**6) # 转换为百万吨
        total_cost.append(current_cost / 10**12)     # 转换为万亿美元
        annual_capacity_log.append(total_annual_mass / 10**6) 
        
        # 检查是否达标
        if current_mass >= TARGET_MASS:
            break
            
    return years, cumulative_mass, total_cost, annual_capacity_log

# ==========================================
# 3. 运行模拟 (Run Simulations)
# ==========================================
res_se_static = simulate_scenario('SE_Static')
res_se_dynamic = simulate_scenario('SE_Dynamic')
res_rocket = simulate_scenario('Rocket_Only')
res_hybrid = simulate_scenario('Hybrid')

# 输出关键结果文本
print(f"--- 模拟结果摘要 ---")
print(f"1. 纯电梯(静态): 完成年份 {res_se_static[0][-1]}, 总成本 ${res_se_static[2][-1]:.2f} T")
print(f"2. 纯电梯(动态): 完成年份 {res_se_dynamic[0][-1]}, 总成本 ${res_se_dynamic[2][-1]:.2f} T")
print(f"3. 纯火箭:       完成年份 {res_rocket[0][-1]}, 总成本 ${res_rocket[2][-1]:.2f} T")
print(f"4. 混合策略:     完成年份 {res_hybrid[0][-1]}, 总成本 ${res_hybrid[2][-1]:.2f} T")

# ==========================================
# 4. 专业绘图 (Plotting)
# ==========================================
plt.figure(figsize=(14, 10)) # 设置画布大小

# 子图1: 累计运输量曲线 (Cumulative Mass)
plt.subplot(2, 2, (1, 2)) # 占据上方整行
plt.plot(res_se_static[0], res_se_static[1][1:], label=f'SE Only (Static) - {res_se_static[0][-1]}', linestyle=':', color='gray', alpha=0.7)
plt.plot(res_se_dynamic[0], res_se_dynamic[1][1:], label=f'SE Only (Dynamic 8%) - {res_se_dynamic[0][-1]}', color='blue', linewidth=2)
plt.plot(res_rocket[0], res_rocket[1][1:], label=f'Rockets Only - {res_rocket[0][-1]}', color='red', linestyle='--')
plt.plot(res_hybrid[0], res_hybrid[1][1:], label=f'Hybrid Strategy (Recommended) - {res_hybrid[0][-1]}', color='green', linewidth=3)

plt.axhline(y=100, color='black', linestyle='-', linewidth=1, label='Target (100M tons)')
plt.title('Figure 1: Progress Towards 100M Tons Goal (Cumulative Mass)', fontsize=14, fontweight='bold')
plt.ylabel('Cumulative Mass (Million Tons)', fontsize=12)
plt.xlabel('Year', fontsize=12)
plt.legend(loc='lower right', fontsize=10)
plt.grid(True, alpha=0.3)
plt.xlim(2050, 2150) # 限制X轴范围以便看清细节

# 子图2: 总成本对比 (Cost Comparison)
plt.subplot(2, 2, 3)
scenarios = ['SE (Static)', 'SE (Dynamic)', 'Rockets', 'Hybrid']
costs = [res_se_static[2][-1], res_se_dynamic[2][-1], res_rocket[2][-1], res_hybrid[2][-1]]
colors = ['gray', 'blue', 'red', 'green']

bars = plt.bar(scenarios, costs, color=colors, edgecolor='black', alpha=0.8)
plt.title('Figure 2: Total Project Cost Estimation', fontsize=14, fontweight='bold')
plt.ylabel('Cost (Trillion USD)', fontsize=12)
plt.grid(axis='y', alpha=0.3)

# 在柱状图上方标注数值
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 2, f'${yval:.1f}T', ha='center', va='bottom', fontweight='bold')

# 子图3: 年运力增长趋势 (Annual Capacity Growth)
plt.subplot(2, 2, 4)
plt.plot(res_se_dynamic[0], res_se_dynamic[3], label='Space Elevator Capacity', color='blue')
plt.plot(res_hybrid[0], res_hybrid[3], label='Hybrid Capacity (Rocket Boost)', color='green', linestyle='--')
plt.title('Figure 3: Annual Transport Capacity Growth', fontsize=14, fontweight='bold')
plt.ylabel('Annual Capacity (Million Tons/Year)', fontsize=12)
plt.xlabel('Year', fontsize=12)
plt.legend()
plt.grid(True, alpha=0.3)
plt.xlim(2050, 2100)

plt.tight_layout()
plt.show()
# plt.savefig('Task1_Analysis.png') # 如果需要保存图片请取消注释