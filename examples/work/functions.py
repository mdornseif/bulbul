def baz():
    pass


#def baz():
#    return  # does not work so far !


def foo():
    a = 1
    a = 2
    return a


def bar(a, b):
    return [a, b]


#def foobar(a, b=1):
#   return [a, b]


def getval(a):
    return 5 - a


def getval2(x):
    # "docstring"
    localvariable2 = 1
    localvariable = 1
    localvariable2 = 2
    return localvariable


#def lam():
#    x = 4
#    return lambda x: z+x


baz()  #  `None` in Python, `undefined` in Javascript
print foo()
print bar(1, 'a')
z = 1 + 2 + getval2(getval(1))
print 1, 2, 3
print z

