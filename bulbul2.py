#!/usr/bin/env python
# Fat-free Python3 to Javascript/ES6 compiler attempt.
# see https://github.com/ahmedaliadeel/bulbul
# bulbul2 is heavily based on astor 0.6 code_gen.
import ast
import astor.code_gen
import json
import sys


from astor.code_gen import Precedence
from astor.code_gen import set_precedence

op_data = """
              Or   ||           1
             And   &&           1
             Not   !            1
              Eq   ==           1
              Gt   >            0
             GtE   >=           0
              In   in           0
              Is   is           0
           NotEq   !=           0
              Lt   <            0
             LtE   <=           0
           NotIn   not in       0
           IsNot   is not       0
           BitOr   |            1
          BitXor   ^            1
          BitAnd   &            1
          LShift   <<           1
          RShift   >>           0
             Add   +            1
             Sub   -            0
            Mult   *            1
             Div   /            0
             Mod   %            0
        FloorDiv   //           0
         MatMult   @            0
          PowRHS                1
          Invert   ~            1
            UAdd   +            0
            USub   -            0
             Pow   **           1
"""

op_data = [x.split() for x in op_data.splitlines()]
op_data = [[x[0], ' '.join(x[1:-1]), int(x[-1])] for x in op_data if x]
for index in range(1, len(op_data)):
    op_data[index][2] *= 2
    op_data[index][2] += op_data[index - 1][2]
symbol_data = dict((getattr(ast, x, None), y) for x, y, z in op_data)


def get_op_symbol(obj, fmt='%s', symbol_data=symbol_data, type=type):
    """Given an AST node object, returns a string containing the symbol.
    """
    return fmt % symbol_data[type(obj)]


shims = set()  # which shims do we need to add

# see https://greentreesnakes.readthedocs.org/en/latest/nodes.html

class BulbulGenerator(astor.code_gen.SourceGenerator):
    def newline(self, node=None, extra=0):
        self.new_lines = max(self.new_lines, 1 + extra)
        if node is not None and self.add_line_information:
            self.write('// line: %s' % node.lineno)
            self.new_lines = 1

    def else_body(self, elsewhat):
        if elsewhat:
            self.write(' else {')
            self.body(elsewhat)
            self.write('\n', '}', '\n')

    def visit_Assign(self, node):
        set_precedence(node, node.value, *node.targets)
        self.newline(node)
        if not hasattr(node, '_scope'):
            node._scope = {'variables': []}
        for target in node.targets:
            if hasattr(target, 'id') and target.id not in node._scope['variables']:
                self.write('var ', target, ' = ')
                node._scope['variables'].append(target.id)
            else:
                self.write(target, ' = ')
        self.visit(node.value)

    def visit_FunctionDef(self, node, async=False):
        scope = {'variables': [], 'functions': []}
        skip_first_arg = False

        if hasattr(node, '_scope'):
            node._scope.setdefault('functions', []).append(node.name)

        if hasattr(node, '_scope'):
            scope = dict(scope, **node._scope)
            if 'isclass' in node._scope:
                skip_first_arg = node._scope['isclass']
        for a in node.body:
            a._scope = scope

        funcname = ('' if skip_first_arg else "function")

        prefix = 'async ' if async else ''
        self.decorators(node, 1)
        self.statement(node, '%s%s %s' % (prefix, funcname, node.name), '(')
        self.visit_arguments(node.args)
        self.write(')')
        self.conditional_write(' ->', self.get_returns(node))
        self.write(' {')
        self.body(node.body)
        self.write('\n', ' }')

    def visit_ClassDef(self, node):
        have_args = []

        def paren_or_comma():
            if have_args:
                self.write(', ')
            else:
                have_args.append(True)
                self.write('(')

        self.decorators(node, 2)
        self.statement(node, 'class %s' % node.name)

        scope = {'isclass': True}
        for b in node.body:
            b._scope = scope

        for base in node.bases:
            self.write(paren_or_comma, base)
        # keywords not available in early version
        for keyword in self.get_keywords(node):
            self.write(paren_or_comma, keyword.arg or '',
                       '=' if keyword.arg else '**', keyword.value)
        self.conditional_write(paren_or_comma, '*', self.get_starargs(node))
        self.conditional_write(paren_or_comma, '**', self.get_kwargs(node))
        self.write(have_args and ') {' or ' {')
        self.body(node.body)
        self.write('\n', '}')

    def visit_If(self, node):
        set_precedence(node, node.test)
        self.statement(node, 'if (', node.test, ') {', '\n')
        self.body(node.body)
        self.statement(node, '\n', '}')
        while True:
            else_ = node.orelse
            if len(else_) == 1 and isinstance(else_[0], ast.If):
                node = else_[0]
                set_precedence(node, node.test)
                self.write('\n', 'else if (', node.test, ') {', '\n')
                self.body(node.body)
                self.statement(node, '\n', '}')
            else:
                self.else_body(else_)
                break

    def visit_NameConstant(self, node):
        self.write(node.value)

    def visit_Pass(self, node):
        self.statement(node, '; //  pass')

    def visit_Print(self, node):
        self.statement(node, 'console.log')
        with self.delimit('()'):
            self.comma_list(node.values)

    def visit_Return(self, node):
        set_precedence(node, node.value)
        self.statement(node, 'return')
        with self.delimit('()'):
            self.conditional_write(node.value)
    # Expressions

    def visit_Attribute(self, node):
        self.write(node.value, '.', node.attr)

    def visit_Call(self, node):
        want_comma = []

        def write_comma():
            if want_comma:
                self.write(', ')
            else:
                want_comma.append(True)

        # special cases for build-ins
        if isinstance(node.func, ast.Attribute):
            name = node.func.attr
            if node.func.attr == 'append':
                node.func.attr = 'push'  # rewrite Method name
        elif isinstance(node.func, ast.Name):
            name = node.func.id
            if node.func.id == 'int':
                node.func.id = "Number"
            if node.func.id == 'object':
                node.func.id = "Object"
            # include shim
            if node.func.id in set(('len', 'sum')):
                shims.add(node.func.id)
            # rewrite to literal
            if node.func.id == 'list':
                with self.delimit('[]'):
                    self.comma_list(node.args)
                return
            if node.func.id == 'dict':
                with self.delimit('{}'):
                    for keyword in node.keywords:
                        # a keyword.arg of None indicates dictionary unpacking
                        # (Python >= 3.5)
                        self.write(write_comma, keyword.arg, ':', keyword.value)
                return

        args = node.args
        keywords = node.keywords
        starargs = self.get_starargs(node)
        kwargs = self.get_kwargs(node)
        numargs = len(args) + len(keywords)
        numargs += starargs is not None
        numargs += kwargs is not None
        p = Precedence.Comma if numargs > 1 else Precedence.call_one_arg
        set_precedence(p, *args)
        if name[0].isupper():
            # we assume this is a class Constructor
            self.write('new ')
        self.visit(node.func)
        self.write('(')
        for arg in args:
            self.write(write_comma, arg)

        set_precedence(Precedence.Comma, *(x.value for x in keywords))
        for keyword in keywords:
            # a keyword.arg of None indicates dictionary unpacking
            # (Python >= 3.5)
            arg = keyword.arg or ''
            self.write(write_comma, arg, '=' if arg else '**', keyword.value)
        # 3.5 no longer has these
        self.conditional_write(write_comma, '*', starargs)
        self.conditional_write(write_comma, '**', kwargs)
        self.write(')')

    def visit_Name(self, node):
        # TODO: visit_NameConst
        # special cases for build-ins
        if node.id == 'True':
            self.write("true")
        elif node.id == 'False':
            self.write("false")
        elif node.id == 'None':
            self.write("null")
        else:
            self.write(node.id)

    def visit_Str(self, node):
        self.write(json.dumps(node.s))

    def visit_Tuple(self, node):
        with self.delimit('[]'):
            self.comma_list(node.elts)

    def visit_BoolOp(self, node):
        with self.delimit(node, node.op) as delimiters:
            op = get_op_symbol(node.op, ' %s ')
            set_precedence(delimiters.p + 1, *node.values)
            for idx, value in enumerate(node.values):
                self.write(idx and op or '', value)

    def visit_UnaryOp(self, node):
        with self.delimit(node, node.op) as delimiters:
            set_precedence(delimiters.p, node.operand)
            # In Python 2.x, a unary negative of a literal
            # number is merged into the number itself.  This
            # bit of ugliness means it is useful to know
            # what the parent operation was...
            node.operand._p_op = node.op
            sym = get_op_symbol(node.op)
            self.write(sym, ' ' if sym.isalpha() else '', node.operand)

    def visit_Compare(self, node):
        with self.delimit(node, node.ops[0]) as delimiters:
            set_precedence(delimiters.p + 1, node.left, *node.comparators)
            self.visit(node.left)
            for op, right in zip(node.ops, node.comparators):
                self.write(get_op_symbol(op, ' %s '), right)

    def visit_Lambda(self, node):
        with self.delimit(node) as delimiters:
            set_precedence(delimiters.p, node.body)
            self.write('lambda ')
            self.visit_arguments(node.args)
            self.write(': ', node.body)

    def visit_ListComp(self, node):
        with self.delimit('[]'):
            self.write(*node.generators)
            self.write(node.elt)


    def visit_IfExp(self, node):
        with self.delimit(node) as delimiters:
            set_precedence(delimiters.p + 1, node.body, node.test)
            set_precedence(delimiters.p, node.orelse)
            self.write(node.test, ' ? ', node.body, ' : ', node.orelse)

    def visit_For(self, node, async=False):
        set_precedence(node, node.target)
        prefix = 'async ' if async else ''
        #self.statement(node, '%sfor (var ' % prefix,
        #               node.target, ' of ', node.iter, ')', '\n')
        #with self.delimit('{}'):
        #    self.body_or_else(node)
        self.statement(node, '%sfor (var ' % prefix,
                       node.target, ' of ', node.iter, ')', '\n')
        self.write('if(', node.iter, '.hasOwnProperty(', node.target, '))')
        with self.delimit('{}'):
            self.body_or_else(node)

    def visit_Module(self, node):
        scope = {'variables': [], 'functions': []}
        for b in node.body:
            b._scope = scope
        self.write(*node.body)
        self.write('\n', '// exports for commonJS')
        for funcname in scope.get('functions', []):
            if not funcname.startswith('_'):
                self.write('\n', 'exports.%s' % funcname, ' = ', funcname)

    def visit_comprehension(self, node):
        set_precedence(node, node.iter, *node.ifs)
        set_precedence(Precedence.comprehension_target, node.target)
        self.write(' for (', node.target, ' of ', node.iter, ')')
        for if_ in node.ifs:
            self.write(' if ', if_)


def to_source(node, indent_with=' ' * 4, add_line_information=False,
              pretty_string=astor.code_gen.pretty_string, pretty_source=astor.code_gen.pretty_source):
    generator = BulbulGenerator(indent_with, add_line_information,
                                pretty_string)
    generator.visit(node)
    generator.result.append('\n')
    return pretty_source(str(s) for s in generator.result)

a = ast.parse(open((sys.argv[1])).read())
#sys.stderr.write((astor.dump(a)) + '\n')
#print '(function() {\n  "use strict";\n'
print "// autogenerated by bulbul2 from", sys.argv[1]
print(to_source(a, add_line_information=False))
#print '\n})();\n'

if shims:
    print "// bulbul2 helper functions"
    if 'len' in shims:
        print "function len(l) { return l.length; };"
    if 'sum' in shims:
        print "function sum(l) { return [0].concat(l).reduce(function(a, b) { return a + b; })};"

