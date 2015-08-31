def mengenvorschlag_helfer(menge, ve):
    rest = menge % ve
    if rest == 0:
        return menge
    if (rest < (ve / 2)) and (menge - rest > 0):
        # abrunden
        return (menge - rest)
    elif False:
        pass
    else:
        # zum naechst passenden Wert aufrunden
        return (menge - rest + ve)
    return menge

print mengenvorschlag_helfer(0, 4)
print mengenvorschlag_helfer(11, 4)
print mengenvorschlag_helfer(12, 4)
print mengenvorschlag_helfer(13, 4)
print mengenvorschlag_helfer(14, 4)
print mengenvorschlag_helfer(15, 4)
print "ja" if True else "nein"
print "ja" if False else "nein"

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
# if not []:
#     print "ok []"
# if []:
#     print "ko []"
if not None:
    print "ok None"
