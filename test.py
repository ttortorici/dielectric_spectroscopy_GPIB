class A:

    class_attr = "inside A"

    def __init__(self, a):
        self.a = a
        print(f"Class attr = {self.__class__.class_attr}")
        print(f"init A with {a}")

    def method_a(self):
        return self.__class__.class_attr

    def __str__(self):
        return "class A"


class B(A):

    class_attr = "inside B"

    def __init__(self):
        super(self.__class__, self).__init__("B")


if __name__ == "__main__":
    b = B()
    print(b.method_a())
    print(b)
