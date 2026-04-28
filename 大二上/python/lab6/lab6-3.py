import re
import datetime
import os

# 全局变量：登录状态
is_login = False
# 文件名变量
u_file = "user_info.txt"
l_file = "log.txt"


def check(u, p):
    """读取 user_info.txt 验证账号密码 (跳过第一行表头)"""
    if not os.path.exists(u_file):
        return False
    with open(u_file, "r", encoding="utf-8") as f:
        # 读取所有行
        lines = f.readlines()
        # 从索引1开始循环（跳过第0行的表头 user_name password）
        for line in lines[1:]:
            # 去除首尾空白并按空格分割
            parts = line.strip().split()
            # 确保这一行至少有两个元素（账号和密码）
            if len(parts) >= 2:
                real_u = parts[0]
                real_p = parts[1]
                if real_u == u and real_p == p:
                    return True
    return False


# --- 装饰器 ---

def auth(func):
    """验证登录装饰器"""

    def wrapper(*args, **kwargs):
        global is_login

        # 如果已经登录，直接运行
        if is_login:
            return func(*args, **kwargs)

        print(f"\n[权限验证] 功能 '{func.__name__}' 需要登录才能操作。")
        while True:
            u = input("请输入用户名: ")
            p = input("请输入密码: ")

            if check(u, p):
                print(">>> 登录成功！")
                is_login = True
                return func(*args, **kwargs)
            else:
                print("[错误] 用户名或密码错误，请重新输入。")

    return wrapper


def log(func):
    """日志记录装饰器"""

    def wrapper(*args, **kwargs):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"Function: {func.__name__} | Time: {now}\n"

        try:
            with open(l_file, "a", encoding="utf-8") as f:
                f.write(msg)
        except Exception as e:
            print(f"[日志错误] 无法写入日志: {e}")

        return func(*args, **kwargs)

    return wrapper


# --- 业务功能 ---

def menu():
    print("\n##################### NKCS InfoSystem V0.1 #####################")
    print("================================================== Powered by Zodiac==")
    print("\n         a : 增加记录")
    print("         d : 删除记录")
    print("         c : 修改记录")
    print("         f : 查找记录")
    print("         s : 展示记录")
    print("         q : 退出系统")
    print("-" * 66)


@auth
@log
def show(lst):
    if not lst:
        print("\n[提示] 通讯录为空。")
        return
    print("\n~~~~~~~~~~~~~~~ 通讯录数据列表 ~~~~~~~~~~~~~~~")
    print("=" * 70)
    print(f"{'No.':<5} {'Name':<15} {'QQ':<15} {'Phone':<15} {'E-mail':<20}")
    print("-" * 70)
    for i, item in enumerate(lst):
        print(f"{i + 1:<5} {item['name']:<15} {item['qq']:<15} {item['phone']:<15} {item['email']:<20}")
    print("=" * 70)


@auth
@log
def add(lst):
    print("\n--- 增加记录 ---")
    while True:
        name = input("请输入姓名: ")
        if name.strip():
            break
        else:
            print("[错误] 姓名不能为空。请重新输入。")
    while True:
        qq = input("请输入QQ: ")
        if qq.isdigit() and len(qq) >= 5:
            break
        else:
            print("[错误] QQ号必须是5位以上的数字。请重新输入。")
    while True:
        phone = input("请输入电话: ")
        if phone.isdigit() and len(phone) >= 7:
            break
        else:
            print("[错误] 电话号码必须是7位以上的数字。请重新输入。")
    reg = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    while True:
        email = input("请输入邮箱: ")
        if re.match(reg, email):
            break
        else:
            print("[错误] 邮箱格式不正确 (例如: user@example.com)。请重新输入。")

    item = {
        'name': name,
        'qq': qq,
        'phone': phone,
        'email': email
    }
    lst.append(item)
    print(f"\n插入成功! 此时表为")
    show(lst)


@auth
@log
def delete(lst):
    print("\n--- 删除记录 ---")
    if not lst:
        print("[提示] 通讯录为空, 无法删除。")
        return
    idx = -1
    while True:
        try:
            s = input("请输入要删除的记录序号: ")
            n = int(s)
            tmp = n - 1
            if 0 <= tmp < len(lst):
                idx = tmp  # 索引有效，赋值并跳出循环
                break
            else:
                print(f"[错误] 序号 {n} 不存在, 请重新输入。")
        except ValueError:
            print("[错误] 输入无效, 请输入一个数字序号。")
    item = lst.pop(idx)
    print(f"\n删除成功 (已删除: {item['name']}), 最新的列表为")
    show(lst)


@auth
@log
def modify(lst):
    print("\n--- 修改记录 ---")
    if not lst:
        print("[提示] 通讯录为空, 无法修改。")
        return
    idx = -1
    while True:
        try:
            s = input("请输入要修改的记录序号: ")
            n = int(s)
            tmp = n - 1
            if 0 <= tmp < len(lst):
                idx = tmp
                break
            else:
                print(f"[错误] 序号 {n} 不存在, 请重新输入。")
        except ValueError:
            print("[错误] 输入无效, 请输入一个数字序号。")

    item = lst[idx]
    print(f"--- 正在修改 [No. {idx + 1}] {item['name']} 的信息 ---")
    print("  n : 修改姓名")
    print("  q : 修改QQ")
    print("  p : 修改电话")
    print("  m : 修改邮箱")
    choice = input("请输入要修改的子项: ").lower()
    flag = False  # 是否修改标记

    if choice == 'n':
        while True:
            val = input("请输入新的姓名 (若不修改请输入空格后回车): ")
            if val == ' ': break
            if val.strip():
                item['name'] = val
                flag = True
                break
            else:
                print("[错误] 姓名不能为空。请重新输入。")
    elif choice == 'q':
        while True:
            val = input("请输入新的QQ (若不修改请输入空格后回车): ")
            if val == ' ': break
            if val.isdigit() and len(val) >= 5:
                item['qq'] = val
                flag = True
                break
            else:
                print("[错误] QQ号必须是5位以上的数字。请重新输入。")
    elif choice == 'p':
        while True:
            val = input("请输入新的电话 (若不修改请输入空格后回车): ")
            if val == ' ': break
            if val.isdigit() and len(val) >= 7:
                item['phone'] = val
                flag = True
                break
            else:
                print("[错误] 电话号码必须是7位以上的数字。请重新输入。")
    elif choice == 'm':
        reg = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        while True:
            val = input("请输入新的邮箱 (若不修改请输入空格后回车): ")
            if val == ' ': break
            if re.match(reg, val):
                item['email'] = val
                flag = True
                break
            else:
                print("[错误] 邮箱格式不正确 (例如: user@example.com)。请重新输入。")
    else:
        print("[错误] 无效的子项选择, 操作取消。")

    if flag:
        print("\n已修改, 最新的列表为")
    else:
        print("\n未做修改, 当前列表为")
    show(lst)


@auth
@log
def find(lst):
    print("\n--- 查找记录 ---")
    if not lst:
        print("[提示] 通讯录为空。")
        return
    idx = -1
    while True:
        try:
            s = input("请输入要查找的记录序号: ")
            n = int(s)
            tmp = n - 1

            if 0 <= tmp < len(lst):
                idx = tmp
                break
            else:
                print(f"[错误] 序号 {n} 不存在, 请重新输入。")
        except ValueError:
            print("[错误] 输入无效, 请输入一个数字序号。")

    item = lst[idx]
    print("\n查找到的记录为:")
    print("=" * 70)
    print(f"{'No.':<5} {'Name':<15} {'QQ':<15} {'Phone':<15} {'E-mail':<20}")
    print("-" * 70)
    print(f"{idx + 1:<5} {item['name']:<15} {item['qq']:<15} {item['phone']:<15} {item['email']:<20}")
    print("=" * 70)


def main():
    # 确保有 user_info.txt 文件，否则无法登录
    if not os.path.exists(u_file):
        print(f"[警告] 未找到 {u_file}，请先创建文件并添加用户数据。")

    data = []  # 存储数据的列表
    while True:
        menu()
        opt = input("请输入功能对应的代号: ").lower()
        if opt == 'a':
            add(data)
        elif opt == 'd':
            delete(data)
        elif opt == 'c':
            modify(data)
        elif opt == 'f':
            find(data)
        elif opt == 's':
            show(data)
        elif opt == 'q':
            print("\n感谢使用，再见！")
            break
        else:
            print("\n[错误] 无效的输入, 请输入 'a', 'd', 'c', 'f', 's' 或 'q'。")

        input("\n--- 按回车键返回主菜单 ---")


if __name__ == "__main__":
    main()