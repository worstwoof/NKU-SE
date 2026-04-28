init=1
day=365
rate_1=0.001
rate_2=0.005
rate_3=0.01
level_up_1=init*(1+rate_1)**day
level_down_1=init*(1-rate_1)**day
level_up_2=init*(1+rate_2)**day
level_down_2=init*(1-rate_2)**day
level_up_3=init*(1+rate_3)**day
level_down_3=init*(1-rate_3)**day

print("问题一：")
print(f"每天进步1‰，一年后的水平是：{level_up_1:.3f}")
print(f"每天退步1‰，一年后的水平是：{level_down_1:.3f}")
print(f"每天进步5‰，一年后的水平是：{level_up_2:.3f}")
print(f"每天退步5‰，一年后的水平是：{level_down_2:.3f}")
print(f"每天进步1%，一年后的水平是：{level_up_3:.3f}")
print(f"每天退步1%，一年后的水平是：{level_down_3:.3f}")
level=init
workday=0
restday=0
for a in range(1,day+1):
    day_week=a%7
    if day_week== 6 or day_week==0:
        level*=(1-rate_3)
        restday+=1
    else:
        level*=(1+rate_3)
        workday+=1
print("问题二：")
print(f"一周5个工作日，每天进步1%，2个休息日，每天退步1%，一年后的结果是：{level:.3f}")

level_A=(1+0.01)**365
rate_B=(level_A/(1-0.01)**restday)**(1/workday)-1
print("问题三：")
print(f"工作日的努力参数是: {rate_B:.3f}")