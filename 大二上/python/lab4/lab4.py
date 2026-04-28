from functools import reduce

# 1. filter,reduce 求素数及其和
print("=== 题目1：求100以内素数的和 ===")
# 判断素数的lambda表达式
is_prime = lambda n: n > 1 and all(n % i != 0 for i in range(2, int(n**0.5) + 1))

# 使用filter求100以内素数
primes = list(filter(is_prime, range(2, 101)))
# 使用reduce计算素数和
prime_sum = reduce(lambda x, y: x + y, primes)

print("100以内素数:", primes)
print("素数和:", prime_sum)
print()


# 2. map 规范姓名
print("=== 题目2：规范姓名格式 ===")
names = ['lisa','JACK','Adam']
normalized_names = list(map(lambda x: x.capitalize(), names))
print("输入:", names)
print("输出:", normalized_names)
print()


# 3. sorted 按照排名对list进行排序
print("=== 题目3：按排名排序 ===")
data = [(1,'byd'),(3,'xiaopeng'),(2,'tesla'),(4,'weilai')]
sorted_data = sorted(data, key=lambda x: x[0])
print("输入:", data)
print("输出:", sorted_data)
print()


# 4. 使用闭包实现步数记录
print("=== 题目4：闭包实现步数记录 ===")
def count_steps(original_step=0):
    steps = original_step  # 保存初始步数
    
    def wrapper(new_steps):
        nonlocal steps  # 声明使用外部变量
        steps += new_steps  # 累加步数
        return steps
    
    return wrapper

count_steps_func = count_steps(10)
print("初始10步，加5步:", count_steps_func(5))   # 输出: 15 (10+5)
print("再加5步:", count_steps_func(5))          # 输出: 20 (15+5)
print("再加8步:", count_steps_func(8))          # 输出: 28 (20+8)