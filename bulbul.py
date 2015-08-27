#!/usr/bin/env python
# Fat-free Python3 to Javascript/ES6 compiler attempt.
# see https://github.com/ahmedaliadeel/bulbul

import ast
import astor  # pip install astor
import json
import sys


# see https://greentreesnakes.readthedocs.org/en/latest/nodes.html
class FirstParser(ast.NodeVisitor):

    def __init__(self):
        pass

    def continue_(self, stmt):
        '''Helper: parse a node's children'''
        return super(FirstParser, self).generic_visit(stmt)

    def parse(self, code):
        '''Parse text into a tree and walk the result'''
        tree = ast.parse(code)
        self.visit(tree)

    def visit(self, node):
        """Dispatches the call to visit_$nodetype method."""
        nodetype = node.__class__.__name__
        f = getattr(self, "visit_" + nodetype, self.generic_visit)
        return f(node)

    def visit_ImportFrom(self, stmt_module):
        # retrieve the name from the returned object
        # normally, there is just a single alias
        listofimports = []
        for imp in stmt_module.names:
            listofimports.append(imp.name)

        if len(listofimports) == 1:
            stmt_module.js = "import %s from '%s';" % (
                ','.join(listofimports),
                str(stmt_module.module).replace('.', '/'))

        else:
            stmt_module.js = "import { %s } from '%s';" % (
                ','.join(listofimports),
                str(stmt_module.module).replace('.', '/'))
        # self.continue_(stmt_module)

    def visit_ClassDef(self, node):
        scope = {'isclass': True}
        for b in node.body:
            b._scope = scope
        self.continue_(node)
        r = ''
        for call in node.decorator_list:
            r += '@%s(%s)\n' % (
                call.func.id,
                ','.join([arg.js for arg in call.args]))
        r += 'class %s {\n' % node.name
        r += ';\n'.join([b.js for b in node.body])
        r += '\n}'
        node.js = r

    def visit_Dict(self, stmt_dict):
        d = {}
        self.continue_(stmt_dict)
        for k, v in zip(stmt_dict.keys, stmt_dict.values):
            # d[k.s] = v.s
            # print (v)
            self.continue_(v)
        for k, v in zip(stmt_dict.keys, stmt_dict.values):
            # d[k.s] = v.s
            d[k.js] = v.js
        stmt_dict.js = json.dumps(d)
        # stmt_dict.js=stmt_dict.js.replace('\\\"', '')

        res = []
        for k, v in zip(stmt_dict.keys, stmt_dict.values):
            # d[k.s] = v.s
            # print (v)
            res.append(k.js+":" + v.js)
        # stmt_dict.js = json.dumps(res)
        # stmt_dict.js=stmt_dict.js.replace('\\\"', '')
        stmt_dict.js = '{'+','.join(res)+'}'
        return stmt_dict

    def visit_List(self, node):
        d = []
        (self.continue_(node))

        for v in node.elts:
            d.append(v.js)
        node.js = '[%s]' % ','.join(d)

    def visit_Module(self, stmt_module):
        scope = {'variables': []}

        for b in stmt_module.body:
            b._scope = scope
            # self.continue_(b)
        (self.continue_(stmt_module))
        for b in stmt_module.body:
            print(b.js)

    def visit_Assign(self, node):
        self.continue_(node)
        node.js = ''
        node.alreadyassigned = []
        lfs = ''
        llist = []
        replace_self_with_this = False
        if hasattr(node, '_scope'):
            if 'isclass' in node._scope:
                replace_self_with_this = node._scope['isclass']
        for t in node.targets:
            if isinstance(t, ast.Attribute):
                # llist.append(('this' if replace_self_with_this else t.value.id )+'.'+t.attr)
                llist.append(
                    "%s.%s" % (
                        ('this' if replace_self_with_this else t.value.js),
                        t.attr)
                )
            else:
                if t.id not in node._scope['variables']:
                    lfs = 'var %s' % t.id  # + ' : any'

                    node._scope['variables'].append(t.id)
                else:
                    llist.append(t.id)

        leftside = lfs + (','.join(llist))
        rightside = (node.value.js)
        node.js = "%s = %s;" % (leftside, rightside)

    def visit_Num(self, node):
        self.continue_(node)
        node.js = (node.n)

    def visit_Str(self, node):
        self.continue_(node)
        node.js = '"%s"' % node.s
        # node.js = node.s
        node.jsvalue = node.s

    def visit_Name(self, node):
        self.continue_(node)
        node.js = str(node.id)

    def visit_NameConstant(self, node):
        self.continue_(node)
        node.js = str(node.value)
        node.jsvalue = node.value
        if str(node.value) == 'True':
            node.js = 'true'
        if str(node.value) == 'False':
            node.js = 'false'

    def visit_Expr(self, node):
        self.continue_(node)
        node.js = (node.value.js)

    def visit_Attribute(self, node):
        self.continue_(node)
        # node.js = (str(node.value.id) if hasattr(node.value, 'id') else '')+"." +str(node.attr)
        # print (node.attr)
        # node.js = (str(node.value.id) if hasattr(node.value, 'id') else node.attr)+"." +str(node.attr)
        # print (str(node.attr))
        node.js = "%s.%s" % (node.value.js, node.attr)
        node.jsvalue = node.js
        # print (node.js)

    def visit_Return(self, node):
        self.continue_(node)

        node.js = ''
        if (hasattr(node.value, 'js')):
            rightside = (node.value.js)
            node.js = 'return %s ;' % rightside

    def visit_Call(self, node):
        self.continue_(node)
        funcname = node.func.js
        # JSX plug
        if funcname == 'bb_jsx':
            funcname = ''
            node.js = "%s " % (
                funcname,
                ','.join([(arg.jsvalue) for arg in node.args])
            )
        elif funcname == 'bb_export':
            node.js = 'export %s;' % ','.join(
                [str(arg.jsvalue) for arg in node.args])
        else:
            # node.js = str(node.func.id if type(node.func)!=ast.Attribute else node.func.value.id)   +'('+','.join([arg.js for arg in node.args])+')'
            node.js = "%s(%s)" % (
                funcname,
                ','.join([str(arg.js) for arg in node.args])
            )

    def visit_FunctionDef(self, node):
        scope = {'variables': []}
        skip_first_arg = False
        if hasattr(node, '_scope'):
            scope = dict(scope, **node._scope)
            if 'isclass' in node._scope:
                skip_first_arg = node._scope['isclass']
        for a in node.body:
            a._scope = scope
            # self.continue_(a)

        self.continue_(node)
        funcname = ('' if skip_first_arg else "function ") + node.name

        if node.name == '__init__':
            funcname = "constructor"
        node.js = "%s(%s) {" % (
            funcname,
            ','.join([arg.arg
                      for arg in node.args.args[1 if skip_first_arg else 0:]])
        )
        for a in node.body:
            node.js += '\n   %s\n' % (a.js)
        node.js += '}'

    def visit_Pass(self, node):
        node.js = ';'

    def visit_Lambda(self, node):
        # scope = {'variables': []}
        # for a in node.body:
        #    a._scope = scope
        # self.continue_(a)
        self.continue_(node)
        node.js = "function (%s) { " % ','.join(
            [arg.arg for arg in node.args.args])
        # for a in node.body:
        node.js += '\n  return %s ;\n}' % (node.body.js)

    def visit_IfExp(self, node):
        self.continue_(node)
        node.js = '(%s ? %s : %s)' % (
            node.test.js,
            node.body.js,
            node.orelse.js)

    def visit_Compare(self, node):
        self.continue_(node)
        node.js = '(%s==%s)' % (
            node.left.js,
            node.comparators[0].js)

    def visit_BinOp(self, stmt_binop):
        opmap = {}
        opmap[str((ast.Add))] = '+'
        opmap[str((ast.Sub))] = '-'
        opmap[str((ast.Div))] = '/'
        self.continue_(stmt_binop)
        stmt_binop.js = "%s%s%s" % (
            stmt_binop.left.js,
            opmap[str(type(stmt_binop.op))],
            stmt_binop.right.js)


class ReactParser(FirstParser):
    pass


x = FirstParser()
if len(sys.argv) > 2:
    if sys.argv[2] == 'ast':
        a = ast.parse(open((sys.argv[1])).read())
        print(astor.dump(a))
else:
    x.parse(open((sys.argv[1])).read())
