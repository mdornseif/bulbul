

print "ja" if True else "nein"
print "ja" if False else "nein"
print "ja" if "True" else "nein"
print "ja" if "False" else "nein"

if not 1:
    print "ko"
if not 0:
    print "ok 0"
if not True:
    print "ko"
if not False:
    print "ok False"
if not [1]:
    print "ko []"
if not []:
    print "ok []"
if []:
    print "ko []"
if not None:
    print "ok None"
