values = [11, 22, 33, 44, 55, 66, 77, 88, 99, 100, 110, 200, 230, 330]

result = {'k1': [], 'k2': []}

for i in values:
    if i > 66:
        result['k1'].append(i)
    else:
        result['k2'].append(i)
print(result)