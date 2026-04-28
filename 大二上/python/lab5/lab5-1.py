def find(nums):
    n=len(nums)
    if n==0: return -1
    if n==1: return 0
    for i in range(n):
        is_valid=True
        for j in range(n):
            if j<i:
                if nums[j]>=nums[i]:
                    is_valid=False
                    break
            if i==j:
                continue
            if j>i:
                if nums[j]<=nums[i]:
                    is_valid = False
                    break
        if is_valid:
            return i
    return -1

nums1 = [6, 3, 4, 9, 1]
print(f"输入: {nums1}")
print(f"输出: {find(nums1)}")


print("-" * 20)


nums2 = [4, 3, 6, 9, 7]
print(f"输入: {nums2}")
print(f"输出: {find(nums2)}")


print("-" * 20)


nums3 = [1, 2, 3, 4, 5]
print(f"输入: {nums3}")
print(f"输出: {find(nums3)}")

