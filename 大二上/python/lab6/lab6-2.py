def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(times):
                print(f"第 {i+1} 次执行")
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(times=3)
def foo():
    print("Hello，World！")

foo()