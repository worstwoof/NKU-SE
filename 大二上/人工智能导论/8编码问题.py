import time
import tracemalloc
import os
import random
from collections import deque
import heapq
import math
from typing import List, Tuple, Optional, Dict, Any
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading


# ======================================================================
# 1. 状态表示类 (NPuzzleState)
# ======================================================================
class NPuzzleState:
    def __init__(self, board: Tuple[int, ...],
                 parent: Optional['NPuzzleState'] = None,
                 move: str = "",
                 g: int = 0):
        """
        初始化一个状态。
        :param board: 棋盘状态 (e.g., (1, 2, 3, 4, 5, 6, 7, 8, 0))
        :param parent: 父状态节点，用于回溯路径
        :param move: 到达此状态的移动 (e.g., "UP", "DOWN")
        :param g: 从初始状态到此状态的实际代价 (路径长度)
        """
        self.board = board
        self.parent = parent
        self.move = move
        self.g = g  # 实际代价 g(n)

        # 预计算 size 和 blank_index，提高效率
        self.size = int(math.sqrt(len(board)))
        try:
            self.blank_idx = self.board.index(0)
        except ValueError:
            raise ValueError(f"棋盘 {board} 中必须包含一个 0 (空格).")

        # f(n) 和 h(n) 将由求解器在外部计算和设置
        self.h = 0  # 启发式代价 h(n)
        self.f = 0  # 评估函数 f(n) = g(n) + h(n)

    def __hash__(self) -> int:
        """使状态可哈希，用于 'visited' 集合"""
        return hash(self.board)

    def __eq__(self, other: object) -> bool:
        """比较两个状态是否相同"""
        return isinstance(other, NPuzzleState) and self.board == other.board

    def __lt__(self, other: 'NPuzzleState') -> bool:
        """
        比较函数，用于优先队列 (heapq)。
        我们比较 f(n) 值。如果 f(n) 相同，A* 会倾向于比较 h(n) 更小的。
        """
        if self.f == other.f:
            return self.h < other.h
        return self.f < other.f

    def pretty_print(self):
        """格式化打印棋盘（用于调试）"""
        for i in range(self.size):
            row = self.board[i * self.size: (i + 1) * self.size]
            print("  ".join(f"{x:2}" if x != 0 else "  " for x in row))
        print("-" * (self.size * 4))

    def reconstruct_path(self) -> List[str]:
        """从当前状态回溯到初始状态，重建路径"""
        path = []
        current = self
        while current.parent:
            path.append(current.move)
            current = current.parent
        return path[::-1]  # 翻转路径，得到从开始到结束的步骤


# ======================================================================
# 2. 求解器类 (PuzzleSolver)
# ======================================================================
class PuzzleSolver:
    """
    N数码问题的求解器（后端）。
    封装了所有搜索算法和辅助函数。
    """

    def __init__(self, initial_board: List[int], goal_board: List[int]):
        if len(initial_board) != len(goal_board):
            raise ValueError("初始状态和目标状态的大小必须一致。")

        self.initial_board = tuple(initial_board)
        self.goal_board = tuple(goal_board)
        self.size = int(math.sqrt(len(self.initial_board)))

        if self.size * self.size != len(self.initial_board):
            raise ValueError("棋盘大小必须是完美的平方数 (e.g., 9, 16)。")

        # 预计算目标状态中，每个数字的位置，用于曼哈顿距离
        self.goal_pos_cache: Dict[int, int] = {
            val: i for i, val in enumerate(self.goal_board)
        }
        self.nodes_expanded = 0
        self.stats = {}

    def get_inversions(self, board: Tuple[int, ...]) -> int:
        """计算逆序数"""
        inversions = 0
        for i in range(len(board)):
            for j in range(i + 1, len(board)):
                if board[i] != 0 and board[j] != 0 and board[i] > board[j]:
                    inversions += 1
        return inversions

    def is_solvable(self) -> bool:
        """检查N数码问题是否可解"""
        inversions = self.get_inversions(self.initial_board)

        if self.size % 2 != 0:  # 奇数网格 (e.g., 3x3)
            return inversions % 2 == 0
        else:  # 偶数网格 (e.g., 4x4)
            blank_idx = self.initial_board.index(0)
            blank_row = blank_idx // self.size  # 0-indexed row from top
            return (inversions + blank_row) % 2 != 0

    def get_neighbors(self, state: NPuzzleState) -> List[NPuzzleState]:
        """(d) 获取一个状态的所有有效邻居状态（可扩展）"""
        neighbors = []
        r, c = divmod(state.blank_idx, self.size)
        moves = [(-1, 0, "UP"), (1, 0, "DOWN"), (0, -1, "LEFT"), (0, 1, "RIGHT")]

        for dr, dc, move_name in moves:
            nr, nc = r + dr, c + dc

            # 检查移动是否在边界内
            if 0 <= nr < self.size and 0 <= nc < self.size:
                new_blank_idx = nr * self.size + nc
                new_board_list = list(state.board)
                # 交换空格和棋子
                new_board_list[state.blank_idx], new_board_list[new_blank_idx] = \
                    new_board_list[new_blank_idx], new_board_list[state.blank_idx]

                neighbors.append(
                    NPuzzleState(
                        board=tuple(new_board_list),
                        parent=state,
                        move=move_name,
                        g=state.g + 1
                    )
                )
        return neighbors

    # --- (c) 启发式函数 ---
    def h_misplaced_tiles(self, board: Tuple[int, ...]) -> int:
        """启发式函数 h1: 错位棋子数"""
        misplaced = 0
        for i in range(len(board)):
            if board[i] != 0 and board[i] != self.goal_board[i]:
                misplaced += 1
        return misplaced

    def h_manhattan_distance(self, board: Tuple[int, ...]) -> int:
        """启发式函数 h2: 曼哈顿距离"""
        distance = 0
        for i in range(len(board)):
            val = board[i]
            if val == 0: continue
            current_r, current_c = divmod(i, self.size)
            goal_idx = self.goal_pos_cache[val]
            goal_r, goal_c = divmod(goal_idx, self.size)
            distance += abs(current_r - goal_r) + abs(current_c - goal_c)
        return distance

    def _apply_move_tuple(self, board_tuple: Tuple[int, ...], move: str) -> Tuple[int, ...]:
        """(f) 辅助函数：对元组状态应用一个移动，用于动画"""
        board_list = list(board_tuple)
        size = self.size
        blank_idx = board_list.index(0)
        r, c = divmod(blank_idx, size)
        moves_map = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}
        dr, dc = moves_map[move]
        nr, nc = r + dr, c + dc
        if 0 <= nr < size and 0 <= nc < size:
            new_blank_idx = nr * size + nc
            board_list[blank_idx], board_list[new_blank_idx] = \
                board_list[new_blank_idx], board_list[blank_idx]
            return tuple(board_list)
        return board_tuple

    def solve(self, algorithm: str,
              heuristic_name: Optional[str] = None,
              max_depth: int = 35) -> Tuple[Optional[List[str]], Dict[str, Any]]:
        """主求解函数，路由到不同的搜索算法"""

        if not self.is_solvable():
            return None, {"error": "不可解"}

        self.nodes_expanded = 0

        # (a, b) 监控内存和时间
        tracemalloc.stop()
        tracemalloc.start()
        start_time = time.perf_counter()

        path = None

        if algorithm == 'bfs':
            path = self._bfs()
        elif algorithm == 'dfs':
            path = self._dfs(max_depth)
        elif algorithm == 'astar':
            if heuristic_name == 'misplaced':
                path = self._heuristic_search(self.h_misplaced_tiles, use_g=True)
            elif heuristic_name == 'manhattan':
                path = self._heuristic_search(self.h_manhattan_distance, use_g=True)
            else:
                raise ValueError("A* 必须指定 'misplaced' 或 'manhattan' 启发式函数。")
        elif algorithm == 'random':
            path = self._random_walk(max_depth)
        else:
            raise ValueError(f"未知算法: {algorithm}")

        end_time = time.perf_counter()
        mem_current, mem_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # (a, b) 收集实验结果
        stats = {
            "algorithm": f"{algorithm}" + (f"_{heuristic_name}" if heuristic_name else ""),
            "nodes_expanded": self.nodes_expanded,
            "time_taken_sec": end_time - start_time,
            "memory_peak_mb": mem_peak / 1024 / 1024,
            "path_length": len(path) if path else 0,
            "path": path,
        }
        return path, stats

    # --- (a) 宽度优先搜索 (BFS) ---
    def _bfs(self) -> Optional[List[str]]:
        initial_state = NPuzzleState(self.initial_board)
        queue = deque([initial_state])
        visited = {initial_state.board}

        while queue:
            current_state = queue.popleft()
            self.nodes_expanded += 1
            if current_state.board == self.goal_board:
                return current_state.reconstruct_path()
            for neighbor in self.get_neighbors(current_state):
                if neighbor.board not in visited:
                    visited.add(neighbor.board)
                    queue.append(neighbor)
        return None

    # --- (b) 深度优先搜索 (DFS / DLS) ---
    def _dfs(self, max_depth: int) -> Optional[List[str]]:
        initial_state = NPuzzleState(self.initial_board)
        stack = [initial_state]
        visited = {initial_state.board: 0}

        while stack:
            current_state = stack.pop()
            self.nodes_expanded += 1
            if current_state.board == self.goal_board:
                return current_state.reconstruct_path()
            if current_state.g >= max_depth:
                continue
            for neighbor in self.get_neighbors(current_state):
                if (neighbor.board not in visited or neighbor.g < visited[neighbor.board]):
                    visited[neighbor.board] = neighbor.g
                    stack.append(neighbor)
        return None

    # --- (c) 启发式搜索 (A*) ---
    def _heuristic_search(self, heuristic_func, use_g: bool) -> Optional[List[str]]:
        initial_state = NPuzzleState(self.initial_board)
        pq: List[Tuple[int, int, NPuzzleState]] = []

        initial_state.h = heuristic_func(initial_state.board)
        initial_state.f = initial_state.g + initial_state.h if use_g else initial_state.h
        heapq.heappush(pq, (initial_state.f, initial_state.h, initial_state))

        visited: Dict[Tuple[int, ...], int] = {initial_state.board: 0}

        while pq:
            f, h, current_state = heapq.heappop(pq)
            self.nodes_expanded += 1
            if current_state.g > visited[current_state.board]:
                continue
            if current_state.board == self.goal_board:
                return current_state.reconstruct_path()

            for neighbor in self.get_neighbors(current_state):
                new_g = neighbor.g
                if (neighbor.board not in visited or new_g < visited[neighbor.board]):
                    visited[neighbor.board] = new_g
                    new_h = heuristic_func(neighbor.board)
                    new_f = (new_g + new_h) if use_g else new_h
                    neighbor.h = new_h
                    neighbor.f = new_f
                    heapq.heappush(pq, (new_f, new_h, neighbor))
        return None

    # --- (d) 随机决策选择 ---
    def _random_walk(self, max_steps: int) -> Optional[List[str]]:
        current_state = NPuzzleState(self.initial_board)
        for _ in range(max_steps):
            self.nodes_expanded += 1
            if current_state.board == self.goal_board:
                return current_state.reconstruct_path()
            neighbors = self.get_neighbors(current_state)
            if not neighbors: break
            current_state = random.choice(neighbors)
        return None


# ======================================================================
# 3. 随机谜题生成器
# ======================================================================
def generate_solvable_puzzle(goal_state: List[int], num_shuffles: int) -> List[int]:
    """
    通过从目标状态开始随机移动 num_shuffles 次来生成一个可解的谜题。
    """
    board = tuple(goal_state)
    size = int(math.sqrt(len(board)))

    last_move_name = None
    moves_info = [
        (-1, 0, "UP", "DOWN"), (1, 0, "DOWN", "UP"),
        (0, -1, "LEFT", "RIGHT"), (0, 1, "RIGHT", "LEFT")
    ]

    for _ in range(num_shuffles):
        blank_idx = board.index(0)
        r, c = divmod(blank_idx, size)

        valid_moves = []
        for dr, dc, move_name, inverse_name in moves_info:
            if move_name == last_move_name:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size:
                valid_moves.append((dr, dc, inverse_name))

        if not valid_moves: continue

        dr, dc, next_last_move_name = random.choice(valid_moves)

        nr, nc = r + dr, c + dc
        new_blank_idx = nr * size + nc

        new_board_list = list(board)
        new_board_list[blank_idx], new_board_list[new_blank_idx] = \
            new_board_list[new_blank_idx], new_board_list[blank_idx]

        board = tuple(new_board_list)
        last_move_name = next_last_move_name

    return list(board)


# ======================================================================
# 4. 交互式 GUI 应用 (PuzzleApp)
# ======================================================================
GOAL_8 = [1, 2, 3, 4, 5, 6, 7, 8, 0]
GOAL_15 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0]
HARDEST_8_STATE = [8, 7, 6, 5, 4, 3, 2, 1, 0]


class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("N-Puzzle 交互式求解器")

        # --- (f) 美化：新的高级感配色 ---
        self.COLOR_PRIMARY = "#2C3A47"
        self.COLOR_ACCENT = "#0078D4"
        self.COLOR_ACCENT_LIGHT = "#EBF5FB"
        self.COLOR_BG_LIGHT = "#F4F6F6"
        self.COLOR_SECONDARY = "#7F8C8D"
        self.COLOR_CANVAS_BG = "#EAECEE"
        self.COLOR_TILE = "#FFFFFF"
        self.COLOR_TILE_TEXT = "#2C3A47"
        self.COLOR_EMPTY_TILE = "#D0D3D4"
        self.COLOR_STATUS_TEXT = "#FFFFFF"
        self.COLOR_BUTTON_TEXT = "#FFFFFF"

        self.root.config(bg=self.COLOR_BG_LIGHT)

        # --- (f) 美化：使用清晰的 Segoe UI 字体 (非粗体) ---
        self.FONT_TITLE = ("Segoe UI", 24)
        self.FONT_LABEL = ("Segoe UI", 14)
        self.FONT_BUTTON = ("Segoe UI", 11)
        self.FONT_RADIO = ("Segoe UI", 10)
        self.FONT_STATUS = ("Segoe UI", 10)
        self.FONT_TILE_BIG = ("Segoe UI", 50)  # 8-Puzzle 字体更大
        self.FONT_TILE_SMALL = ("Segoe UI", 40)  # 15-Puzzle 字体更大
        self.FONT_RESULT = ("Consolas", 10)

        self.solver: Optional[PuzzleSolver] = None
        self.solution_path: Optional[List[str]] = None
        self.animation_state: List[Any] = [None, 0]
        self.current_board_size = 3
        self.animation_job = None

        # --- (f) 升级：更大的瓦片尺寸 ---
        self.TILE_SIZE = 120  # 8-Puzzle 瓦片尺寸
        self.MARGIN = 15

        self.main_frame = tk.Frame(root, bg=self.COLOR_BG_LIGHT)
        self.main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        self.left_frame = tk.Frame(self.main_frame, bg=self.COLOR_BG_LIGHT)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # --- (f) 升级：更宽的右侧面板 ---
        self.right_frame = tk.Frame(self.main_frame, bg=self.COLOR_BG_LIGHT, width=400)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        self.right_frame.pack_propagate(False)

        self.create_styles()
        self.create_controls()
        self.create_display()
        self.create_status_bar()

        # --- (f) 升级：更大的窗口 ---
        self.center_window(1200, 900)

        self.generate_new_puzzle(3)

    def create_styles(self):
        """配置 ttk 组件的统一样式"""
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Custom.TLabelframe',
                        background=self.COLOR_BG_LIGHT,
                        bordercolor=self.COLOR_SECONDARY,
                        relief='flat')
        style.configure('Custom.TLabelframe.Label',
                        font=self.FONT_LABEL,
                        foreground=self.COLOR_PRIMARY,
                        background=self.COLOR_BG_LIGHT)

        style.configure('TButton',
                        background=self.COLOR_ACCENT,
                        foreground=self.COLOR_BUTTON_TEXT,
                        font=self.FONT_BUTTON,
                        relief='flat',
                        padding=12)
        style.map('TButton',
                  background=[('active', self.COLOR_PRIMARY)],
                  foreground=[('disabled', '#ADADAD')])

        style.configure('TRadiobutton',
                        background=self.COLOR_BG_LIGHT,
                        foreground=self.COLOR_PRIMARY,
                        font=self.FONT_RADIO)
        style.map('TRadiobutton',
                  background=[('active', self.COLOR_ACCENT_LIGHT)])

    def create_controls(self):
        """创建右侧的控制面板"""
        control_frame = ttk.LabelFrame(self.right_frame, text="控制面板", style='Custom.TLabelframe')
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        gen_frame = tk.Frame(control_frame, bg=self.COLOR_BG_LIGHT)
        gen_frame.pack(fill=tk.X, pady=5)

        self.btn_gen8 = ttk.Button(gen_frame, text="生成 8-Puzzle")
        self.btn_gen8.config(command=lambda: self.generate_new_puzzle(3))
        self.btn_gen8.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)

        self.btn_gen15 = ttk.Button(gen_frame, text="生成 15-Puzzle")
        self.btn_gen15.config(command=lambda: self.generate_new_puzzle(4))
        self.btn_gen15.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)

        # --- (e) 新增 "Hardest 8-Puzzle" 按钮 ---
        hardest_frame = tk.Frame(control_frame, bg=self.COLOR_BG_LIGHT)
        hardest_frame.pack(fill=tk.X, pady=(0, 5))

        self.btn_gen_hardest = ttk.Button(hardest_frame, text="加载最难 8-Puzzle (31步)")
        self.btn_gen_hardest.config(command=self.generate_hardest_puzzle)
        self.btn_gen_hardest.pack(expand=True, fill=tk.X, padx=5, pady=5)
        # --- 新增结束 ---

        anim_frame = ttk.LabelFrame(self.right_frame, text="动画演示", style='Custom.TLabelframe')
        anim_frame.pack(fill=tk.X, padx=10, pady=10)

        self.animation_mode = tk.StringVar(value="manual")

        ttk.Radiobutton(
            anim_frame,
            text="手动步进 (按 Enter)",
            variable=self.animation_mode,
            value="manual",
            style='TRadiobutton'
        ).pack(anchor=tk.W, padx=15, pady=5)

        ttk.Radiobutton(
            anim_frame,
            text="自动播放 (500ms)",
            variable=self.animation_mode,
            value="auto",
            style='TRadiobutton'
        ).pack(anchor=tk.W, padx=15, pady=5)

        solve_frame = ttk.LabelFrame(self.right_frame, text="求解算法", style='Custom.TLabelframe')
        solve_frame.pack(fill=tk.X, padx=10, pady=10)

        self.solve_buttons = {}
        algorithms = [
            ("A* (Manhattan)", "astar_manhattan", ("astar", "manhattan")),
            ("A* (Misplaced)", "astar_misplaced", ("astar", "misplaced")),
            ("BFS (宽度优先)", "bfs", ("bfs", None)),
            ("DFS (深度限制)", "dfs", ("dfs", None)),
            ("Random (随机)", "random", ("random", None)),
        ]

        for name, key, (alg, heur) in algorithms:
            btn = ttk.Button(solve_frame, text=name, command=lambda a=alg, h=heur: self.solve_puzzle_threaded(a, h))
            btn.pack(fill=tk.X, padx=5, pady=4)
            self.solve_buttons[key] = btn

        result_frame = ttk.Frame(self.right_frame, relief="solid", borderwidth=1, style='Custom.TLabelframe')
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            font=self.FONT_RESULT,
            wrap=tk.WORD,
            bg="#FFFFFF",
            fg=self.COLOR_PRIMARY,
            relief="flat",
            borderwidth=0,
            highlightthickness=0
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

    def create_display(self):
        """创建左侧的显示区域（标题和画布）"""
        display_frame = tk.Frame(self.left_frame, bg=self.COLOR_BG_LIGHT)
        display_frame.pack(fill=tk.BOTH, expand=True)

        self.animation_label_var = tk.StringVar()
        self.animation_label = tk.Label(
            display_frame,
            textvariable=self.animation_label_var,
            font=self.FONT_TITLE,
            bg=self.COLOR_BG_LIGHT,
            fg=self.COLOR_PRIMARY,
            wraplength=600,  # 增加换行宽度
            justify=tk.CENTER
        )
        self.animation_label.pack(pady=20)

        canvas_container = tk.Frame(display_frame, bg=self.COLOR_CANVAS_BG)
        canvas_container.pack(expand=True, padx=10, pady=10)

        self.canvas_width = 4 * 120 + 2 * self.MARGIN  # 最大尺寸 (4x 120px tile)
        self.canvas_height = self.canvas_width
        self.canvas = tk.Canvas(
            canvas_container,
            width=self.canvas_width,
            height=self.canvas_height,
            bg=self.COLOR_CANVAS_BG,
            highlightthickness=0,
            relief="flat"
        )
        self.canvas.pack()

    def create_status_bar(self):
        """创建底部的状态栏"""
        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪。请生成一个谜题。")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.FLAT,
            anchor=tk.W,
            font=self.FONT_STATUS,
            bg=self.COLOR_ACCENT,
            fg=self.COLOR_STATUS_TEXT,
            padx=10, pady=5
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def generate_new_puzzle(self, size: int):
        """(d) 生成一个新的随机谜题"""
        self.status_var.set(f"正在生成 {size}x{size} 谜题...")
        self.root.update_idletasks()
        self.set_buttons_state(tk.DISABLED)

        if self.animation_job:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None
        self.root.unbind("<Return>")

        self.current_board_size = size
        goal = GOAL_8 if size == 3 else GOAL_15

        if size == 3:
            steps = random.randint(8, 20)
            self.TILE_SIZE = 120
            self.FONT_TILE = self.FONT_TILE_BIG
        else:
            steps = random.randint(20, 35)
            self.TILE_SIZE = 90
            self.FONT_TILE = self.FONT_TILE_SMALL

        new_canvas_width = size * self.TILE_SIZE + 2 * self.MARGIN
        self.canvas.config(width=new_canvas_width, height=new_canvas_width)

        initial_board = generate_solvable_puzzle(goal, steps)
        self.solver = PuzzleSolver(initial_board, goal)
        self.solution_path = None

        self.draw_board(self.solver.initial_board, new_canvas_width, new_canvas_width)
        self.animation_label_var.set(f"{size}x{size} 谜题已生成 (约 {steps} 步)")
        self.result_text.delete('1.0', tk.END)
        self.status_var.set("谜题已生成。请选择一个算法进行求解。")
        self.set_buttons_state(tk.NORMAL)

    def generate_hardest_puzzle(self):
        """(e) 加载 8-Puzzle 最长链 (31步)"""
        self.status_var.set("正在加载最难 8-Puzzle (31 步)...")
        self.root.update_idletasks()
        self.set_buttons_state(tk.DISABLED)

        if self.animation_job:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None
        self.root.unbind("<Return>")

        self.current_board_size = 3
        goal = GOAL_8
        initial_board = HARDEST_8_STATE

        self.TILE_SIZE = 120
        self.FONT_TILE = self.FONT_TILE_BIG

        new_canvas_width = 3 * self.TILE_SIZE + 2 * self.MARGIN
        self.canvas.config(width=new_canvas_width, height=new_canvas_width)

        self.solver = PuzzleSolver(initial_board, goal)
        self.solution_path = None

        self.draw_board(self.solver.initial_board, new_canvas_width, new_canvas_width)
        self.animation_label_var.set("最难 8-Puzzle (31 步) 已加载")
        self.result_text.delete('1.0', tk.END)
        self.status_var.set("最难谜题已加载。请选择 A* (Manhattan) 求解。")
        self.set_buttons_state(tk.NORMAL)

    def solve_puzzle_threaded(self, alg: str, heur: Optional[str] = None):
        """在子线程中启动求解，防止GUI卡死"""
        if not self.solver:
            return

        self.set_buttons_state(tk.DISABLED)

        if self.animation_job:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None
        self.root.unbind("<Return>")

        alg_name = f"{alg}" + (f"_{heur}" if heur else "")
        self.status_var.set(f"正在使用 {alg_name} 求解...")
        self.root.update_idletasks()
        self.solution_path = None
        self.result_text.delete('1.0', tk.END)
        self.animation_label_var.set(f"正在使用 {alg_name} 求解...")

        is_hard = self.solver.size > 3

        if (alg == 'bfs' or alg == 'dfs') and is_hard:
            stats = {"algorithm": alg_name, "error": "Skipped (too hard)"}
            self._solve_callback(None, stats)
        else:
            t = threading.Thread(target=self._solve_logic, args=(alg, heur), daemon=True)
            t.start()

    def _solve_logic(self, alg: str, heur: Optional[str]):
        """[子线程] 实际执行求解的函数"""
        if not self.solver:
            return
        max_depth = 30 if self.solver.size == 3 else 50
        path, stats = self.solver.solve(alg, heuristic_name=heur, max_depth=max_depth)
        # 将结果交还给主线程处理
        self.root.after(0, self._solve_callback, path, stats)

    def _solve_callback(self, path: Optional[List[str]], stats: Dict[str, Any]):
        """[主线程] 求解完成后的回调函数，用于更新GUI"""
        self.result_text.delete('1.0', tk.END)

        if "error" in stats:
            self.result_text.insert(tk.END, f"算法: {stats['algorithm']}\n")
            self.result_text.insert(tk.END, f"状态: {stats['error']}\n")
            self.status_var.set("求解被跳过（问题太难）。")
            self.animation_label_var.set("求解被跳过")
        else:
            self.result_text.insert(tk.END, f"算法: {stats['algorithm']}\n")
            self.result_text.insert(tk.END, f"路径长度: {stats['path_length']} 步\n")
            self.result_text.insert(tk.END, f"搜索节点: {stats['nodes_expanded']} 个\n")
            self.result_text.insert(tk.END, f"耗时: {stats['time_taken_sec']:.4f} 秒\n")
            self.result_text.insert(tk.END, f"峰值内存: {stats['memory_peak_mb']:.4f} MB\n")

            if path:
                self.solution_path = path
                self.animation_label_var.set("求解成功！")

                if self.animation_mode.get() == "manual":
                    self.status_var.set(f"求解成功！发现 {len(path)} 步。按 Enter 键演示。")
                    self.start_manual_animation()
                else:
                    self.status_var.set(f"求解成功！发现 {len(path)} 步。正在自动播放...")
                    self.start_auto_animation()
            else:
                self.status_var.set("求解失败：未找到路径。")
                self.animation_label_var.set("求解失败")

        self.set_buttons_state(tk.NORMAL)

    def set_buttons_state(self, state: str):
        """启用或禁用所有控制按钮"""
        self.btn_gen8.config(state=state)
        self.btn_gen15.config(state=state)
        self.btn_gen_hardest.config(state=state)
        for btn in self.solve_buttons.values():
            btn.config(state=state)

    def draw_board(self, board_state: Tuple[int, ...], canvas_width=None, canvas_height=None):
        """(f) 在画布上绘制棋盘，并确保其居中"""
        self.canvas.delete("all")
        if not self.solver:
            return

        size = self.solver.size

        if canvas_width is None:
            canvas_width = int(self.canvas.cget('width'))
        if canvas_height is None:
            canvas_height = int(self.canvas.cget('height'))

        grid_pixel_width = size * self.TILE_SIZE
        grid_pixel_height = size * self.TILE_SIZE

        start_x = (canvas_width - grid_pixel_width) / 2
        start_y = (canvas_height - grid_pixel_height) / 2

        for i, val in enumerate(board_state):
            r, c = divmod(i, size)

            x1 = start_x + c * self.TILE_SIZE
            y1 = start_y + r * self.TILE_SIZE
            x2 = x1 + self.TILE_SIZE
            y2 = y1 + self.TILE_SIZE

            fill_color = self.COLOR_EMPTY_TILE if val == 0 else self.COLOR_TILE

            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=fill_color,
                outline=self.COLOR_SECONDARY,
                width=1
            )

            if val != 0:
                self.canvas.create_text(
                    (x1 + x2) / 2, (y1 + y2) / 2,
                    text=str(val),
                    font=self.FONT_TILE,
                    fill=self.COLOR_TILE_TEXT
                )

    def start_manual_animation(self):
        """(f) 启动手动步进（Enter）动画"""
        if not self.solution_path or not self.solver:
            return

        self.animation_state = [self.solver.initial_board, 0]
        self.animation_label_var.set(f"初始状态 (0/{len(self.solution_path)})：等待中\n(按 Enter 键开始演示)")
        self.draw_board(self.solver.initial_board)

        self.root.bind("<Return>", self.next_step_on_enter)
        self.root.focus_force()

    def next_step_on_enter(self, event):
        """(f) 手动步进的下一步逻辑"""
        if not self.solution_path or not self.solver:
            return

        current_board, step_index = self.animation_state

        if step_index < len(self.solution_path):
            move = self.solution_path[step_index]
            self.animation_label_var.set(f"第 {step_index + 1}/{len(self.solution_path)} 步: {move}\n(按 Enter 键继续)")

            next_board = self.solver._apply_move_tuple(current_board, move)
            self.draw_board(next_board)

            self.animation_state[0] = next_board
            self.animation_state[1] = step_index + 1

            if self.animation_state[1] == len(self.solution_path):
                self.animation_label_var.set("目标已达成！\n(按 Enter 键结束)")

        else:
            self.animation_label_var.set(f"动画演示完成。\n请选择新的谜题或算法。")
            self.root.unbind("<Return>")
            self.set_buttons_state(tk.NORMAL)

    def start_auto_animation(self):
        """(f) 启动自动播放动画"""
        if not self.solution_path or not self.solver:
            return

        self.animation_state = [self.solver.initial_board, 0]
        self.animation_label_var.set(f"初始状态 (0/{len(self.solution_path)})：自动播放中...")
        self.draw_board(self.solver.initial_board)

        self.animation_job = self.root.after(1000, self.update_auto_animation)

    def update_auto_animation(self):
        """(f) 自动播放的循环逻辑"""
        if not self.solution_path or not self.solver:
            self.animation_job = None
            return

        current_board, step_index = self.animation_state

        if step_index < len(self.solution_path):
            move = self.solution_path[step_index]
            self.animation_label_var.set(f"第 {step_index + 1}/{len(self.solution_path)} 步: {move}")

            next_board = self.solver._apply_move_tuple(current_board, move)
            self.draw_board(next_board)

            self.animation_state[0] = next_board
            self.animation_state[1] = step_index + 1

            self.animation_job = self.root.after(500, self.update_auto_animation)
        else:
            self.animation_label_var.set("目标已达成！")
            self.status_var.set("自动播放完成。")
            self.animation_job = None
            self.set_buttons_state(tk.NORMAL)

    def center_window(self, width, height):
        """将窗口居中显示"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))


if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()