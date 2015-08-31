a = ['a']
b = [1, 2]
c = list()
d = list([1, 2, 3])

def append(f):
    return ["FUNC", f]

print append(1)
a.append('b')
print a
# print d[-1] # broken
# print d.pop()
