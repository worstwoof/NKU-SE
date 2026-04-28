f = open('hamlet.txt', 'r', encoding='utf-8')
t = f.read()
f.close()

t = t.lower()

s = "!\"#$%&()*+,-./:;<=>?@[\\]^_‘{|}~"

for x in s:
    t = t.replace(x, ' ')

words = t.split()

d = {}
for w in words:
    if w in d:
        d[w] += 1
    else:
        d[w] = 1

L = list(d.items())
L.sort(key=lambda x: x[1], reverse=True)

for i in range(10):
    print(L[i][0], L[i][1])