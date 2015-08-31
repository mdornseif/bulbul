for x in range(3):
    print x

print [int(x) for x in '123456'.split()]
print [int(x) for x in '123456'.split() if x != '3' or x != 2]
