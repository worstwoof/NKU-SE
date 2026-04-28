import math

class Circle:
    def __init__(self, radius):

        self.radius = radius

    def get_perimeter(self):
        result = 2 * math.pi * self.radius
        return round(result, 2)

    def get_area(self):
        result = math.pi * (self.radius ** 2)
        return round(result, 2)

if __name__ == "__main__":
    r = float(input("请输入圆的半径: "))
    c = Circle(r)

    print(f"圆的半径: {c.radius}")
    print(f"圆的周长: {c.get_perimeter()}")
    print(f"圆的面积: {c.get_area()}")