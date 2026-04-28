data = [1, 2, 3, 4, 2, 1, 5, 6, 5]
new_data=list(set(data))
print(f"原列表: {data}")
print(f"Set去重: {new_data}")
data = [1, 2, 3, 4, 2, 1, 5, 6, 5]
new_data = []
for item in data:
    if item not in new_data:
        new_data.append(item)
print(f"循环去重: {new_data}")
data = [1, 2, 3, 4, 2, 1, 5, 6, 5]
new_data = list(dict.fromkeys(data))
print(f"Dict去重: {new_data}")