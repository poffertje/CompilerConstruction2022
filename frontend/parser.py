import subprocess
import ply.yacc as yacc
import ast
from lexer import tokens, create_lexer, token_error
from util import LocationError, FatalError


# operator precedence as per http://www.swansontec.com/sopc.html
precedence = (
    ('nonassoc', 'IF'),
    ('nonassoc', 'ELSE'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NE'),
    ('left', 'LT', 'GT', 'LE', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULO'),
    ('right', 'NOT', 'UMINUS', 'INV'),
    ('left', 'LBRACKET'),
)


#
# Grammar rules. These adhere closely to the grammar as specified in the
# Language Reference. `p[0]` is the result of the rule assigned to the left-hand
# side of the ':'. `p[1]` is the result of the first element in the right-hand
# side of the rule, and `len(p)` is used to determine which rule was produced in
# a disjunction. A left hand size can be specified multiple times, this is
# equivalent to using a '|'.
#


def p_program(p):
    '''program : declarations'''
    p[0] = ast.Program(p[1]).at(loc(p))


# use left-recursion because we are building an LR(1) parser
def p_declarations(p):
    '''declarations : declaration
                    | declarations declaration'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


def p_declaration(p):
    '''declaration : globaldec
                   | globaldef
                   | fundec
                   | fundef'''
    p[0] = p[1]


def p_globaldec(p):
    '''globaldec : EXTERN type ID SEMICOL'''
    p[0] = ast.GlobalDec(p[2], p[3]).at(loc(p, 3))


def p_globaldef(p):
    '''globaldef : STATIC type ID ASSIGN expr SEMICOL
                 | type ID ASSIGN expr SEMICOL'''
    l = len(p)
    p[0] = ast.GlobalDef(l == 7, p[l - 5], p[l - 4], p[l - 2]).at(loc(p, -4))


def p_fundec(p):
    '''fundec : EXTERN funheader SEMICOL
              | EXTERN funheader_varargs SEMICOL'''
    p[0] = ast.FunDec(*p[2]).at(loc(p, 2, 2))


def p_fundef(p):
    '''fundef : funheader LBRACE RBRACE
              | funheader LBRACE statements RBRACE'''
    name, _type = p[1]
    body = ast.Block(p[3] if len(p) == 5 else [])
    p[0] = ast.FunDef(False, name, _type, body).at(loc(p, 1))


def p_fundef_static(p):
    '''fundef : STATIC funheader LBRACE RBRACE
              | STATIC funheader LBRACE statements RBRACE'''
    name, _type = p[2]
    body = ast.Block(p[4] if len(p) == 6 else [])
    p[0] = ast.FunDef(True, name, _type, body).at(loc(p, 2))


def p_funheader(p):
    '''funheader : type ID LPAREN RPAREN
                 | type ID LPAREN params RPAREN'''
    params = p[4] if len(p) == 6 else []
    p[0] = (p[2], ast.FunType(p[1], params, False).at(loc(p, 2)))


def p_funheader_varargs(p):
    '''funheader_varargs : type ID LPAREN DOTS RPAREN
                         | type ID LPAREN params COMMA DOTS RPAREN'''
    params = p[4] if len(p) == 8 else []
    p[0] = (p[2], ast.FunType(p[1], params, True).at(loc(p, 2)))


def p_params(p):
    '''params : type ID
              | params COMMA type ID'''
    if len(p) == 3:
        p[0] = [ast.Param(p[1], p[2]).at(loc(p, 2))]
    else:
        p[0] = p[1] + [ast.Param(p[3], p[4]).at(loc(p, 4))]


def p_statements(p):
    '''statements : statement
                  | statements statement'''
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]


def p_block(p):
    '''statement : LBRACE RBRACE
                 | LBRACE statements RBRACE'''
    stat = [] if len(p) == 3 else p[2]
    p[0] = ast.Block(stat).at(loc(p))


def p_vardef(p):
    '''statement : type ID ASSIGN expr SEMICOL'''
    p[0] = ast.VarDef(p[1], p[2], p[4]).at(loc(p, 2))


def p_allocation(p):
    '''statement : type LBRACKET expr RBRACKET ID SEMICOL'''
    p[0] = ast.ArrayDef(ast.ArrayType.get(p[1]), p[3], p[5]).at(loc(p, 5))


def p_assignment(p):
    '''statement : ID ASSIGN expr SEMICOL
                 | index ASSIGN expr SEMICOL'''
    ref = p[1]
    if isinstance(ref, str):
        ref = ast.VarUse(ref).at(loc(p, 1))
    p[0] = ast.Assignment(ref, p[3]).at(loc(p))


def p_modification(p):
    '''statement : ID MODIFY expr SEMICOL
                 | index MODIFY expr SEMICOL'''
    ref = p[1]
    if isinstance(ref, str):
        ref = ast.VarUse(ref).at(loc(p, 1))
    op = ast.Operator.get(p[2][:-1])
    p[0] = ast.Modification(ref, op, p[3]).at(loc(p))


def p_expr_statement(p):
    '''statement : expr SEMICOL'''
    p[0] = ast.ExprStatement(p[1]).at(loc(p))


def p_if(p):
    '''statement : IF LPAREN expr RPAREN statement                %prec IF
                 | IF LPAREN expr RPAREN statement ELSE statement %prec ELSE'''
    nobody = block(p[7]) if len(p) == 8 else None
    p[0] = ast.If(p[3], block(p[5]), nobody).at(loc(p, 1, 4))


def block(stat):
    if isinstance(stat, ast.Block):
        return stat
    assert isinstance(stat, ast.Statement)
    return ast.Block([stat]).at(stat)


def p_return(p):
    '''statement : RETURN SEMICOL
                 | RETURN expr SEMICOL'''
    p[0] = ast.Return(p[2] if len(p) == 4 else None).at(loc(p, 1, -2))


def p_varuse(p):
    '''expr : ID'''
    p[0] = ast.VarUse(p[1]).at(loc(p))


def p_index(p):
    '''index : expr LBRACKET expr RBRACKET
       expr : index'''
    base = p[1]
    if len(p) == 2:
        p[0] = base
    elif isinstance(base, ast.VarUse) and base.index is None:
        base.index = p[3]
        p[0] = base.at(loc(p))
    else:
        p[0] = ast.Index(base, p[3]).at(loc(p))


def p_paren(p):
    '''expr : LPAREN expr RPAREN'''
    p[0] = p[2]


def p_binop(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr
            | expr MODULO expr
            | expr EQ expr
            | expr NE expr
            | expr LT expr
            | expr GT expr
            | expr LE expr
            | expr GE expr
            | expr AND expr
            | expr OR expr'''
    p[0] = ast.BinaryOp(p[1], ast.Operator.get(p[2]), p[3]).at(loc(p))


def p_unop(p):
    '''expr : NOT expr
            | MINUS expr %prec UMINUS
            | INV expr'''
    p[0] = ast.UnaryOp(ast.Operator.get(p[1]), p[2]).at(loc(p))


def p_funcall(p):
    '''expr : funcall
       funcall : ID LPAREN RPAREN
               | ID LPAREN exprs RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ast.FunCall(p[1], [] if len(p) == 4 else p[3]).at(loc(p, 1))


def p_exprs(p):
    '''exprs : expr
             | exprs COMMA expr'''
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]


def p_boolconst(p):
    '''expr : BOOLCONST'''
    p[0] = ast.BoolConst(p[1] == 'true').at(loc(p))


def p_charconst(p):
    '''expr : CHARCONST'''
    p[0] = ast.CharConst(p[1]).at(loc(p))


def p_intconst(p):
    '''expr : INTCONST'''
    p[0] = ast.IntConst(int(p[1])).at(loc(p))


def p_hexconst(p):
    '''expr : HEXCONST'''
    p[0] = ast.HexConst(int(p[1][2:], 16)).at(loc(p))


def p_stringconst(p):
    '''expr : STRINGCONST'''
    p[0] = ast.StringConst(p[1])
    sloc = list(loc(p))
    sloc[2] -= 1
    sloc[4] = sloc[2] + len(str(p[0])) - 1
    p[0].at(sloc)


def p_type(p):
    '''type : TYPE
            | type BRACKETS'''
    if len(p) == 2:
        p.last_type_loc = loc(p)
        p[0] = ast.Type.get(p[1])
    else:
        p.last_type_loc = p.last_type_loc[:3] + loc(p, 2)[3:]
        p[0] = ast.ArrayType.get(p[1])


def p_error(t):
    if t is None:
        raise EOFError()
    raise token_error(t, 'Syntax error at \'%s\'' % t.value)


def lhs(p):
    return p.slice[0].type


def loc(p, start=None, end=None):
    '''
    pack the source location of production rule elements into a location tuple:
    (filename, line_start, column_start, line_end, column_end).
    `p` is the production rule, `start` and `end` are the indices in the rule
    between which to span the source location.
    '''
    def column(index):
        pos = p.lexpos(index)
        last_cr = max(p.parser.input.rfind('\n', 0, pos), 1)
        return pos - last_cr

    def unpack(index, list_index):
        if index < 0:
            index += len(p)

        token = p[index]

        if isinstance(token, list):
            assert len(token) > 0
            token = token[list_index]

        if isinstance(token, tuple):
            assert len(token) == 2
            token = token[1]

        return index, token

    if start is None and end is None:
        start = 1
        end = -1
    elif end is None:
        end = start
    assert start is not None

    start, pstart = unpack(start, 0)
    end, pend = unpack(end, -1)

    if isinstance(pstart, ast.Node):
        ystart, xstart  = pstart.location[1:3]
    else:
        ystart = p.lineno(start)
        xstart = column(start)

    if isinstance(pend, ast.Node):
        yend, xend  = pend.location[3:]
    else:
        yend = p.linespan(end)[1]
        xend = column(end) + len(pend) - 1

    return p.lexer.fname, ystart, xstart, yend, xend


def create_parser(**kwargs):
    # disable parsetab.py creation because it seems to make things slower
    parser = yacc.yacc(write_tables=False, **kwargs)
    return parser


def parse(fname, src, debug=False, parser=None):
    lexer = create_lexer(fname)
    if parser is None:
        parser = create_parser(debug=debug)
    parser.input = src
    return parser.parse(src, lexer=lexer, debug=False)


def preprocess(fname, src, include_paths=[]):
    args = ['cpp', '-nostdinc', '-C', '-traditional-cpp']

    for path in include_paths:
        args.append('-I' + path)

    if fname == '<stdin>':
        src = bytearray(src, 'utf-8')
    else:
        args.append(fname)
        src = None

    try:
        proc = subprocess.run(args, input=src, stdout=subprocess.PIPE)
        proc.check_returncode()
        return proc.stdout.decode()
    except subprocess.CalledProcessError as e:
        raise FatalError('preprocessor failed with nonzero exit code')


if __name__ == '__main__':
    import sys
    from util import PrintTree

    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            fname = sys.argv[1]
            src = f.read()
    else:
        fname = '<stdin>'
        src = sys.stdin.read()

    try:
        tree = parse(fname, preprocess(fname, src), debug=False)
        print(tree)
        PrintTree().visit(tree)
        tree.verify()
    except EOFError:
        print('Syntax error: unexpected end of file', file=sys.stderr)
        sys.exit(1)
    except LocationError as e:
        e.print(True, src)
        sys.exit(1)
    except FatalError as e:
        print('Error: %s' % e, file=sys.stderr)
        sys.exit(1)
