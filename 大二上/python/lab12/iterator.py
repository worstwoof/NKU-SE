import time
import tracemalloc
import os

filepath = './log.txt'

print(f"{'='*20} 实验开始 {'='*20}")

print("\n>>> 方法 1: 直接读取所有行到列表 (List)")

tracemalloc.start()
start_time = time.time()

with open(filepath, 'r') as f:
    lines = f.readlines()

end_time = time.time()
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"耗时: {end_time - start_time:.6f} 秒")
print(f"内存占用峰值: {peak / 1024 / 1024:.6f} MB")

print("\n>>> 方法 2: 自定义迭代器逐行读取 (Custom Iterator)")

class LineIterator:
    def __init__(self, filepath):
        ## your code
        self.file = open(filepath, 'r')

    def __iter__(self):
        return self

    def __next__(self):

        line = self.file.readline()
        if line:
            return line
        else:
            self.file.close()
            raise StopIteration


tracemalloc.start()
start_time = time.time()

line_iter = LineIterator(filepath)

end_time = time.time()
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"耗时: {end_time - start_time:.6f} 秒")
print(f"内存占用峰值: {peak / 1024 / 1024:.6f} MB")

print("\n>>> 方法 3: 生成器筛选 'Create' 日志 (Generator)")

def line_generator(filepath):
    with open(filepath, 'r') as file:
        for line in file:
            if 'Create' in line:
                yield line


line_gen = line_generator(filepath)

print("筛选结果示例 (前5条):")
count = 0
for line in line_gen:
    print(line.strip())
    count += 1
    if count >= 5:
        break
