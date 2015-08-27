a = 1
b = 'a'
c = 1.2
d = True  # produces invalid js
# e = (1, 2)
f = ['a']
# g = (1, 2)
h = [1, 2]
i = {'a': 'b'}
j = {'a': 1}
# k = {'a', 'b'}
# l = {'a', 1}
m = list()
n = dict()
o = dict(a='b')  # does not work
p = set()
q = set('a', 1)

def foo():
    return 1

# def bar(a, b):
#     return [a, b]

# def bar(a, b=1):
#    return [a, b]

# def getval(a):
#     return 5 - a

def getval2():
    # "docstring"
    localvariable2 = 1
    localvariable = 1
    localvariable2 = 2
    return localvariable

# def lam():
 #    x = 4
 #    return lambda x: z+x

# z = 1 + 2 + getval2(getval())

class Fooclass(object):
    "docstring"
    pass
    # classvar = 1  # does not work
#    def method(self):
#        return 2
#    def method2(self, a):
#        return a


a = FooClass()
a.b = 'c'
