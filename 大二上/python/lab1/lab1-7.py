x,y=map(int,input().split(','))
a=max(x,y)
for b in range(a,x*y+1):
    if b%x==0 and b%y==0:
        print(b)
        exit()