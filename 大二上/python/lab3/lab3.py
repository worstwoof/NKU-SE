import re

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

def show(contacts):
    if not contacts:
        print("\n[提示] 通讯录为空。")
        return
    print("\n~~~~~~~~~~~~~~~ 通讯录数据列表 ~~~~~~~~~~~~~~~")
    print("=" * 70)
    print(f"{'No.':<5} {'Name':<15} {'QQ':<15} {'Phone':<15} {'E-mail':<20}")
    print("-" * 70)
    for i, record in enumerate(contacts):
        print(f"{i + 1:<5} {record['name']:<15} {record['qq']:<15} {record['phone']:<15} {record['email']:<20}")
    print("=" * 70)


def add(contacts):
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
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    while True:
        email = input("请输入邮箱: ")
        if re.match(email_regex, email):
            break
        else:
            print("[错误] 邮箱格式不正确 (例如: user@example.com)。请重新输入。")
    new_contact = {
        'name': name,
        'qq': qq,
        'phone': phone,
        'email': email
    }
    contacts.append(new_contact)
    print(f"\n插入成功! 此时表为")
    show(contacts)

def delete(contacts):
    print("\n--- 删除记录 ---")
    if not contacts:
        print("[提示] 通讯录为空, 无法删除。")
        return
    index_to_del = -1
    while True:
        try:
            serial_num_str = input("请输入要删除的记录序号: ")
            serial_num_int = int(serial_num_str)
            temp_index = serial_num_int - 1
            if 0 <= temp_index < len(contacts):
                index_to_del = temp_index  # 索引有效，赋值并跳出循环
                break
            else:
                print(f"[错误] 序号 {serial_num_int} 不存在, 请重新输入。")
        except ValueError:
            print("[错误] 输入无效, 请输入一个数字序号。")
    removed_contact = contacts.pop(index_to_del)
    print(f"\n删除成功 (已删除: {removed_contact['name']}), 最新的列表为")
    show(contacts)

def modify(contacts):
    print("\n--- 修改记录 ---")
    if not contacts:
        print("[提示] 通讯录为空, 无法修改。")
        return
    index_to_mod = -1
    while True:
        try:
            serial_num_str = input("请输入要修改的记录序号: ")
            serial_num_int = int(serial_num_str)
            temp_index = serial_num_int - 1
            if 0 <= temp_index < len(contacts):
                index_to_mod = temp_index
                break
            else:
                print(f"[错误] 序号 {serial_num_int} 不存在, 请重新输入。")
        except ValueError:
            print("[错误] 输入无效, 请输入一个数字序号。")
    record = contacts[index_to_mod]
    print(f"--- 正在修改 [No. {index_to_mod + 1}] {record['name']} 的信息 ---")
    print("  n : 修改姓名")
    print("  q : 修改QQ")
    print("  p : 修改电话")
    print("  m : 修改邮箱")
    sub_choice = input("请输入要修改的子项: ").lower()
    modified = False
    if sub_choice == 'n':
        while True:
            new_value = input("请输入新的姓名 (若不修改请输入空格后回车): ")
            if new_value == ' ':
                break
            if new_value.strip():
                record['name'] = new_value
                modified = True
                break
            else:
                print("[错误] 姓名不能为空。请重新输入。")
    elif sub_choice == 'q':
        while True:
            new_value = input("请输入新的QQ (若不修改请输入空格后回车): ")
            if new_value == ' ':
                break
            if new_value.isdigit() and len(new_value) >= 5:
                record['qq'] = new_value
                modified = True
                break
            else:
                print("[错误] QQ号必须是5位以上的数字。请重新输入。")
    elif sub_choice == 'p':
        while True:
            new_value = input("请输入新的电话 (若不修改请输入空格后回车): ")
            if new_value == ' ':
                break
            if new_value.isdigit() and len(new_value) >= 7:
                record['phone'] = new_value
                modified = True
                break
            else:
                print("[错误] 电话号码必须是7位以上的数字。请重新输入。")
    elif sub_choice == 'm':
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        while True:
            new_value = input("请输入新的邮箱 (若不修改请输入空格后回车): ")
            if new_value == ' ':
                break
            if re.match(email_regex, new_value):
                record['email'] = new_value
                modified = True
                break
            else:
                print("[错误] 邮箱格式不正确 (例如: user@example.com)。请重新输入。")
    else:
        print("[错误] 无效的子项选择, 操作取消。")
    if modified:
        print("\n已修改, 最新的列表为")
    else:
        print("\n未做修改, 当前列表为")
    show(contacts)

def find(contacts):
    print("\n--- 查找记录 ---")
    if not contacts:
        print("[提示] 通讯录为空。")
        return
    index_to_find = -1
    while True:
        try:
            serial_num_str = input("请输入要查找的记录序号: ")
            serial_num_int = int(serial_num_str)
            temp_index = serial_num_int - 1

            if 0 <= temp_index < len(contacts):
                index_to_find = temp_index
                break
            else:
                print(f"[错误] 序号 {serial_num_int} 不存在, 请重新输入。")
        except ValueError:
            print("[错误] 输入无效, 请输入一个数字序号。")

    record = contacts[index_to_find]
    print("\n查找到的记录为:")
    print("=" * 70)
    print(f"{'No.':<5} {'Name':<15} {'QQ':<15} {'Phone':<15} {'E-mail':<20}")
    print("-" * 70)
    print(f"{index_to_find + 1:<5} {record['name']:<15} {record['qq']:<15} {record['phone']:<15} {record['email']:<20}")
    print("=" * 70)


def main():
    contacts_list = []
    while True:
        menu()
        choice = input("请输入功能对应的代号: ").lower()
        if choice == 'a':
            add(contacts_list)
        elif choice == 'd':
            delete(contacts_list)
        elif choice == 'c':
            modify(contacts_list)
        elif choice == 'f':
            find(contacts_list)
        elif choice == 's':
            show(contacts_list)
        elif choice == 'q':
            print("\n感谢使用，再见！")
            break
        else:
            print("\n[错误] 无效的输入, 请输入 'a', 'd', 'c', 'f', 's' 或 'q'。")

        input("\n--- 按回车键返回主菜单 ---")


if __name__ == "__main__":
    main()