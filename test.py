import difflib
import os
import subprocess
import sys

pyerrors = []
jserrors = []
for dirname, dirnames, filenames in os.walk(sys.argv[1]):
    # print path to all filenames.
    for filename in filenames:
        name = os.path.join(dirname, filename)
        command = "python %s" % name
        print "#", command
        try:
            pyoutput = subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError:
            print "ERROR"
            pyerrors.append(name)
        command = "python bulbul2.py %s | babel --optional es7.comprehensions | node" % name
        print "#", command
        try:
            jsoutput = subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError:
            print "ERROR"
            jserrors.append(name)
        # we ignore whitespace
        pyoutput = ''.join(pyoutput).replace(' ', '')
        jsoutput = ''.join(jsoutput).replace(' ', '')
        if jsoutput != pyoutput:
            print "WARNING"
            diff = difflib.unified_diff(pyoutput.splitlines(), jsoutput.splitlines())
            print '\n'.join(diff)

if pyerrors:
    print "pyerrors in %s" % ' '.join(pyerrors)
if jserrors:
    print "jserrors in %s" % ' '.join(jserrors)
