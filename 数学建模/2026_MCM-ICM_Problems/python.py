import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import lognorm
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches
import matplotlib.patheffects as path_effects

# ================= 1. 高级绘图设置 =================
sns.set_context("talk", font_scale=1.0)
sns.set_style("white", {
    "axes.grid": True,
    "grid.linestyle": "--",
    "grid.color": "#e0e0e0",
    "axes.spines.top": False,
    "axes.spines.right": False
})
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False

# 配色方案
COLOR_DATA_KDE = "#214a75"
COLOR_DATA_HIST = "#6baed6"
COLOR_RISK_LINE = "#c0392b"
COLOR_RISK_FILL = "#e74c3c"
COLOR_ACCENT_95 = "#f39c12"

# ================= 2. 模拟参数 =================
np.random.seed(42)
N_SIMULATIONS = 10000
daily_demand = 10000
p_failure_annual = 0.10
sigma = 0.9
scale = 21.3

# ================= 3. 运行模拟 =================
def run_simulation():
    max_deficits = []
    for _ in range(N_SIMULATIONS):
        if np.random.rand() < p_failure_annual:
            repair_days = lognorm.rvs(s=sigma, scale=scale)
            repair_days = np.clip(repair_days, 1, 365)
            max_deficits.append(repair_days * daily_demand)
        else:
            max_deficits.append(0)
    return np.array(max_deficits)

deficits = run_simulation()

# ================= 4. 统计分析 =================
risk_events = deficits[deficits > 0]
p95 = np.percentile(deficits, 95)
p999 = np.percentile(deficits, 99.9)
equiv_days = p999 / daily_demand

risk_events_m = risk_events / 1e6
p95_m = p95 / 1e6
p999_m = p999 / 1e6

# ================= 5. 绘图执行 =================
fig, ax = plt.subplots(figsize=(12, 7), dpi=200)

# 5.1 绘制基础数据
sns.histplot(risk_events_m, bins=65, color=COLOR_DATA_HIST, alpha=0.5,
             stat='density', label='Simulated Disruption Scenarios (N=10k)', zorder=2, ax=ax)
sns.kdeplot(risk_events_m, color=COLOR_DATA_KDE, linewidth=3, zorder=3, ax=ax, clip=(0, 4.0))

# 5.2 高亮风险区域
for rect in ax.patches:
    if rect.get_x() + rect.get_width() / 2 > p999_m:
        rect.set_facecolor(COLOR_RISK_FILL)
        rect.set_alpha(0.7)

# ================= 标注位置调整 =================

# --- A. 黄色 95% 线与文本 (保持在右侧) ---
ax.axvline(p95_m, color=COLOR_ACCENT_95, linestyle=':', linewidth=2, zorder=4)
ax.text(p95_m + 0.05, ax.get_ylim()[1]*0.6,
        '95% Threshold\n(Typical Risks)',
        color=COLOR_ACCENT_95, ha='left', va='center', fontweight='bold', fontsize=11)

# --- B. 红色 99.9% 线与方框 (增加间距) ---
ax.axvline(p999_m, color=COLOR_RISK_LINE, linestyle='-', linewidth=3, zorder=5,
           path_effects=[path_effects.withStroke(linewidth=6, foreground='white', alpha=0.5)])

title_text = "DECISION: Required Safety Stock ($S_{buffer}^*$)"
body_text = (f"Confidence Level: 99.9%\n"
             f"Quantity: {p999_m:.2f} Million MT\n"
             f"Buffer Capacity: ~{equiv_days:.0f} Days")

bbox_args = dict(boxstyle="round,pad=0.6,rounding_size=0.3",
                 fc="#fffafa", ec=COLOR_RISK_LINE, lw=2, alpha=1.0)

# 坐标基准
box_x = p999_m + 0.15
box_y = ax.get_ylim()[1] * 0.45

# 1. 绘制正文方框 (保持不变)
ax.text(box_x, box_y, body_text,
        ha='left', va='top', fontsize=12, bbox=bbox_args, zorder=10)

# 2. 绘制标题 (【修改点】：增加垂直间距)
# 在 box_y 的基础上加上 0.15 的高度偏移量，让标题悬浮在方框上方，不紧贴
title_gap = 0.15
ax.text(box_x + 0.04, box_y + title_gap, title_text,
        color=COLOR_RISK_LINE, ha='left', va='bottom', fontweight='bold', fontsize=13, zorder=11)

# --- C. 底部长尾箭头 ---
ax.annotate('Long-tail "Black Swan" Risks\n(Extreme, Low-Probability Events)',
            xy=(3.5, 0.00002), xytext=(2.8, 0.2),
            arrowprops=dict(facecolor='black', arrowstyle='->', connectionstyle="arc3,rad=-0.1", lw=1.5),
            fontsize=11, style='italic', ha='center')

# ================= 6. 装饰 =================
ax.set_title('Stochastic Determination of Minimal Safety Stock', fontsize=18, fontweight='bold', y=1.05)
plt.suptitle('Monte Carlo Simulation based on Interruption Risk Model (Task II)', y=0.95, fontsize=14, color='#555555')

ax.set_xlabel('Potential Cumulative Supply Deficit (Million MT)', fontsize=14, fontweight='medium', labelpad=10)
ax.set_ylabel('Probability Density Function (PDF)', fontsize=14, fontweight='medium', labelpad=10)

ax.set_xlim(0, 4.2)
ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f M'))

legend = ax.legend(loc='upper right', frameon=True, fancybox=True, framealpha=0.9)
legend.get_frame().set_linewidth(0.0)

plt.tight_layout()
plt.savefig('Final_Spaced_Layout.png', dpi=300, bbox_inches='tight')
plt.show()