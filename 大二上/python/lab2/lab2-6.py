a=int(input())
if a==0 or a==1:
    print(f"{a}不是素数")
    exit()
for i in range(2,a):
    if a%i==0:
        print(f"{a}不是素数")
        exit()
print(f"{a}是素数")