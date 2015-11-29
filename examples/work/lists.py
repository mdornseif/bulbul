a = ['a']
b = [1, 2]
c = list()
d = list([1, 2, 3])

def foo(f):
    return ["FUNC", f]

print foo(1)
a.append('b')
print a

def comperend1(data):
    summen1 = []
    for line in data.values():
        summen1.append(line.menge * line.einzelpreis)
    return sum(summen1)


def comperend2(data):
    summen2 = [line.menge * line.einzelpreis for line in data.values()]
    return sum(summen2)


class Test():
    pass

a = Test()
a.menge = 5
a.einzelpreis = 3
b = Test()
b.menge = 7
b.einzelpreis = 13

print comperend1(dict(a=a, b=b))
print comperend2(dict(a=a, b=b))
