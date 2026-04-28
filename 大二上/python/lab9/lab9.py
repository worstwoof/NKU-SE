import sys


class Campus:
    def __init__(self, name):
        self.name = name
        self.income = 0.0
        self.stus = []
        self.tchrs = []
        self.staff = []
        self.courses = []

    def stats(self):
        return f"【{self.name}】 营收:{self.income} | 生:{len(self.stus)} | 师:{len(self.tchrs)} | 员:{len(self.staff)}"


class Person:
    def __init__(self, name, phone, campus):
        self.name = name
        self.phone = phone
        self.campus = campus


class Student(Person):
    def __init__(self, name, phone, campus, sid):
        super().__init__(name, phone, campus)
        self.sid = sid
        self.courses = []

    def add_course(self, course):
        if course not in self.courses:
            self.courses.append(course)
            course.stus.append(self)
            self.campus.income += course.price
            print(f"缴费成功: {course.price}")

    def quit(self):
        if self in self.campus.stus:
            self.campus.stus.remove(self)
        for c in self.courses:
            if self in c.stus:
                c.stus.remove(self)
        self.courses = []
        print("已退学")


class Teacher(Person):
    def __init__(self, name, phone, campus, eid):
        super().__init__(name, phone, campus)
        self.eid = eid
        self.courses = []


class Employee(Person):
    def __init__(self, name, phone, campus, eid, role):
        super().__init__(name, phone, campus)
        self.eid = eid
        self.role = role


class Logistics(Employee):
    def __init__(self, name, phone, campus, eid):
        super().__init__(name, phone, campus, eid, "后勤")


class Finance(Employee):
    def __init__(self, name, phone, campus, eid):
        super().__init__(name, phone, campus, eid, "财务")


class Admin(Employee):
    def __init__(self, name, phone, campus, eid):
        super().__init__(name, phone, campus, eid, "行政")


class Course:
    def __init__(self, name, price, campus):
        self.name = name
        self.price = price
        self.campus = campus
        self.tchr = None
        self.stus = []

    def set_tchr(self, tchr):
        self.tchr = tchr
        tchr.courses.append(self)


class Context:
    def __init__(self):
        self.camps = [Campus(n) for n in ["总部", "北京", "上海", "深圳"]]

    def get_camp(self, idx):
        return self.camps[idx] if 0 <= idx < len(self.camps) else None


class App:
    def __init__(self):
        self.ctx = Context()

    def menu(self):
        print("\n=== 系统菜单 ===")
        print("1. 校区概览")
        print("2. 教师管理")
        print("3. 课程管理")
        print("4. 学生管理")
        print("5. 员工管理")
        print("0. 退出")

    def sel_camp(self):
        for i, c in enumerate(self.ctx.camps):
            print(f"{i}. {c.name}")
        try:
            return self.ctx.get_camp(int(input("序号: ")))
        except:
            return None

    def op_camp(self):
        for c in self.ctx.camps:
            print(c.stats())

    def op_tchr(self):
        opt = input("1.添加 2.列表: ")
        if opt == '1':
            c = self.sel_camp()
            if c:
                t = Teacher(input("名: "), input("电: "), c, input("工号: "))
                c.tchrs.append(t)
        elif opt == '2':
            for c in self.ctx.camps:
                for t in c.tchrs:
                    cs = ",".join([x.name for x in t.courses])
                    print(f"[{c.name}] {t.name} | 课:{cs}")

    def op_course(self):
        opt = input("1.添加 2.定师 3.查生: ")
        if opt == '1':
            c = self.sel_camp()
            if c:
                crs = Course(input("课名: "), float(input("价: ")), c)
                c.courses.append(crs)
        elif opt == '2':
            all_c = [x for camp in self.ctx.camps for x in camp.courses]
            for i, x in enumerate(all_c): print(f"{i}. {x.name}")
            crs = all_c[int(input("选课: "))]

            ts = crs.campus.tchrs
            for i, t in enumerate(ts): print(f"{i}. {t.name}")
            crs.set_tchr(ts[int(input("选师: "))])
        elif opt == '3':
            all_c = [x for camp in self.ctx.camps for x in camp.courses]
            for i, x in enumerate(all_c): print(f"{i}. {x.name}")
            crs = all_c[int(input("选课: "))]
            for s in crs.stus: print(f"- {s.name}")

    def op_stu(self):
        opt = input("1.报名 2.退学 3.查询: ")
        if opt == '1':
            c = self.sel_camp()
            if c:
                s = Student(input("名: "), input("电: "), c, input("学号: "))
                c.stus.append(s)
                for i, x in enumerate(c.courses): print(f"{i}. {x.name} ${x.price}")
                idx = input("课号(逗号隔开): ")
                if idx:
                    for i in idx.split(","): s.add_course(c.courses[int(i)])
        elif opt == '2':
            sid = input("学号: ")
            for c in self.ctx.camps:
                for s in c.stus:
                    if s.sid == sid: s.quit()
        elif opt == '3':
            nm = input("姓名: ")
            for c in self.ctx.camps:
                for s in c.stus:
                    if s.name == nm:
                        print(f"[{c.name}] {s.name} 课:{len(s.courses)}")

    def op_staff(self):
        opt = input("1.添加 2.列表: ")
        if opt == '1':
            c = self.sel_camp()
            if c:
                nm, eid = input("名: "), input("工号: ")
                tp = input("1.后勤 2.财务 3.行政: ")
                if tp == '1':
                    c.staff.append(Logistics(nm, "0", c, eid))
                elif tp == '2':
                    c.staff.append(Finance(nm, "0", c, eid))
                elif tp == '3':
                    c.staff.append(Admin(nm, "0", c, eid))
        elif opt == '2':
            for c in self.ctx.camps:
                for e in c.staff: print(f"[{c.name}] {e.name}-{e.role}")

    def run(self):
        while True:
            self.menu()
            k = input("指令: ")
            if k == '1':
                self.op_camp()
            elif k == '2':
                self.op_tchr()
            elif k == '3':
                self.op_course()
            elif k == '4':
                self.op_stu()
            elif k == '5':
                self.op_staff()
            elif k == '0':
                break


if __name__ == "__main__":
    App().run()