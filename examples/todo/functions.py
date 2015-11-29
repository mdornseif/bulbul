def baz():
    return  # does not work so far !

def foobar(a, b=1):
   return [a, b]

def lam(z):
    x = 4
    return lambda x: z + x

def tup():
    1, 2


print baz()
print foobar(1, 'a')
print lam(4)

