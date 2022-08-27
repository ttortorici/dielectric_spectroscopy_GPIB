from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QAction
import sys


class Signaler1(QWidget):
    signal = Signal(list)


class Doer(QWidget):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.signaler = Signaler1()
        self.signaler.signal.connect(self.write)

    @Slot(list)
    def write(self, list_to_write: list):
        for item in list_to_write:
            print(item)

class Holder:
    def __init__(self, signaler: Signaler1):
        signaler.signal.emit([1,2,3,4,5,6])


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


class A1:
    def __init__(self, name):
        self.name = name
        self.self = "A1"

class A2:
    def __init__(self, name):
        self.name = name
        self.self = "A2"


if __name__ == "__main__":
    x = 0
    if x:
        C=A1
    else:
        C=A2
    c=C("test")
    print(c.name)
    print(c.self)