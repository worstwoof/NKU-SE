
t = (10, 20, 30, 40, 50)

print("索引:", t[0])
print("长度:", len(t))
print("切片:", t[1:4])

print("-" * 20)

print("添加前:", t)

temp = list(t)
temp.append(60)
t = tuple(temp)

print("添加后:", t)

print("-" * 20)

t1 = (1, 2)
t2 = (3, 4)


res1 = t1 + t2
print("元组连接:", res1)

print("-" * 20)

l = ['a', 'b']  # 列表
t = ('c', 'd')  # 元组


res2 = l + list(t)

print("列表+元组:", res2)