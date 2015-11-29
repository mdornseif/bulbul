def outer():
    x = 1
    def inner():
        x = 2
        print "inner:", x
    inner()
    print "outer:", x
    return 'aaaBBB'
print outer()
