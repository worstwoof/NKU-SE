a,b,c,d=map(float,input().split(','))
bmi=d/(c*c)
tizhi=1.2*bmi+0.23*b-5.4-10.8*a
if (a==1 or a==0)and(b>0 and b<150)and(c>0 and c<3)and(d>0 and d<300):
    if a==1:
        if tizhi>=15 and tizhi<=18:
            print("先生你好，恭喜你，身体非常健康")
        if tizhi<15:
            print("先生您好，请注意，你的身体偏瘦")
        if tizhi>18:
            print("先生您好，请注意，你的身体偏胖")

    elif a==0:
        if tizhi >= 25 and tizhi <= 28:
            print("女士你好，恭喜你，身体非常健康")
        if tizhi < 25:
            print("女士您好，请注意，你的身体偏瘦")
        if tizhi > 28:
            print("女士您好，请注意，你的身体偏胖")
elif a!=1 and a!=0:
    print("输入中的性别项输出有误，请检查后再次输入")
elif b>=150:
    print("疑似输入年龄有误，请检查后再次输入")
elif c>=3:
    print("疑似输入身高有误，请检查后再次输入")
elif d>=300:
    print("疑似输入体重有误，请检查后再次输入")