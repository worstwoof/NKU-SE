import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# --- 设置绘图风格与字体 ---
plt.style.use('ggplot')
# 尝试设置中文字体，防止中文标题报错（如果系统无此字体会自动回退）
try:
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial']
    plt.rcParams['axes.unicode_minus'] = False
except:
    pass


def plot_9_charts_final(csv_file):
    print(f"正在读取文件: {csv_file} ...")

    # 1. 读取数据
    try:
        df = pd.read_csv(csv_file)
        # 去除列名可能存在的空格
        df.columns = df.columns.str.strip()
    except Exception as e:
        print(f"读取失败: {e}")
        return

    # 2. 定义映射关系
    # 场景映射：CSV中的 1, 2, 3 -> 文件名中的 Test1, Test2, Test3
    scenario_map = {1: 'Test1', 2: 'Test2', 3: 'Test3'}

    # 操作映射：输出名 -> CSV列名
    op_map = {
        'Insert': 'InsertTime(ms)',
        'Search': 'SearchTime(ms)',
        'Delete': 'DeleteTime(ms)'
    }

    # 算法样式定义 (根据 CSV 中的 Algorithm 列值)
    # 你的CSV中算法名为: BST, AVL, RB_Tree, B_Tree_512
    styles = {
        'BST': {'color': 'grey', 'marker': 'x', 'label': 'BST'},
        'AVL': {'color': 'blue', 'marker': 'o', 'label': 'AVL'},
        'RB_Tree': {'color': 'green', 'marker': 's', 'label': 'RB-Tree'},
        'B_Tree_512': {'color': 'red', 'marker': '^', 'label': 'B-Tree (512)'}
    }

    # 3. 创建输出目录
    output_dir = "imgs_generated"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("开始生成图表...")

    # 4. 循环绘图
    for s_val, s_name in scenario_map.items():
        # 筛选当前场景的数据
        df_scenario = df[df['Scenario'] == s_val]

        if df_scenario.empty:
            print(f"警告: 场景 {s_val} 没有数据，跳过。")
            continue

        for op_name, col_name in op_map.items():
            plt.figure(figsize=(7, 5))

            # 绘制每种算法的曲线
            for algo_name, style in styles.items():
                df_algo = df_scenario[df_scenario['Algorithm'] == algo_name].sort_values(by='N')

                if df_algo.empty:
                    continue

                x = df_algo['N']
                y = df_algo[col_name]

                # 特殊处理 BST: 如果数值太大(>3000ms)，设为 NaN 以免压缩其他曲线
                if algo_name == 'BST':
                    y = y.copy()  # 避免 SettingWithCopy 警告
                    y[y > 3000] = np.nan

                # 只有当有有效数据时才绘制
                if not y.isna().all():
                    plt.plot(x, y,
                             label=style['label'],
                             color=style['color'],
                             marker=style['marker'],
                             linewidth=1.5,
                             markersize=5)

            # 图表装饰
            plt.title(f"{s_name} - {op_name} Performance", fontsize=12)
            plt.xlabel("Data Size (N)")
            plt.ylabel("Time (ms)")
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()

            # 保存文件
            filename = f"{s_name}_{op_name}.png"
            save_path = os.path.join(output_dir, filename)
            plt.savefig(save_path, dpi=300)
            plt.close()
            print(f"已生成: {save_path}")

    print(f"\n全部完成！9张图片已保存在 '{output_dir}' 文件夹中。")


if __name__ == "__main__":
    plot_9_charts_final('tree_performance.csv')