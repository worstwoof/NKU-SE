def sushu(i):
    for j in range(2,i):
        if i%j==0:
            return False
    return True
n=int(input())
for i in range(n//2+1):
    if sushu(i) and sushu(n-i):
        print(f"{n}={i}+{n-i}")
