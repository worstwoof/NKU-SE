def repeat(func):
    def wrapper(*args, **kwargs):
        for i in range(5):
            print(f"第 {i + 1} 次执行")
            func(*args, **kwargs)

    return wrapper

@repeat
def hello(name):
    print(f"Hello, {name}!")

hello("World")