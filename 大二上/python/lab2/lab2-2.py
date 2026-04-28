year=int(input())
if year%4!=0:
    print(f"{year}不是闰年")
    exit()
if year%4==0 and year%100!=0:
    print(f"{year}是闰年")
    exit()
if year%100==0 and year%400!=0:
    print(f"{year}不是闰年")
    exit()
if year%400==0:
    print(f"{year}是闰年")
    exit()