from time import perf_counter


def test(target, args=(), attempts=1000000):
    start = perf_counter()
    for _ in range(attempts):
        target(*args)
    elapsed = perf_counter() - start
    print(elapsed)


if __name__ == "__main__":
    def q1(string):
        return [num.strip() for num in string.replace('",', '').replace('"', '').split(',')]
    def q2(string):
        return [string[0:8].strip(), string[13:25].strip(), string[30:42].strip(), string[43:52].strip()]
    def q3(string):
        l = string.split(",")
        return [l[0].strip(), l[2].strip(), l[4].strip(), l[5].strip()]
    def f1(string):
        return [float(num) for num in string.replace('",', '').replace('"', '').split(',')]
    def f2(string):
        return [float(string[0:8]), float(string[13:25]), float(string[30:42]), float(string[43:52])]

    q = ' 14000.0," ", 0.9977124  ," ",-0.0000264  , 1.00    '
    test(q1, (q,))
    test(q2, (q,))
    test(q3, (q,))
    test(f1, (q,))
    test(f2, (q,))
