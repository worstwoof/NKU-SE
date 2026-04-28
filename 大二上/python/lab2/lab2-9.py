def hanoi(n,source,auxiliary,destination):
    if n==1:
        print(f"{source} --> {destination}")
        return
    hanoi(n-1,source,destination,auxiliary)
    print(f"{source} --> {destination}")
    hanoi(n - 1, auxiliary, source, destination)
n=int(input())
hanoi(n,'A','B','C')