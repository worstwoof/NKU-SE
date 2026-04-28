a=int(input())
list=[]
while a>0:
    list.append(a%10)
    a=a//10
n=len(list)
for i in range(n):
    for j in range(0,n-i-1):
        if list[j]<list[j+1]:
            list[j],list[j+1]=list[j+1],list[j]
result=0
for i in list:
    result=result*10+i
print(result)