import ply.lex as lex
from util import LocationError
from ast import StringConst


# define separate states for parsing strings and multi-line comments, since
# other tokens like keywords have no special meaning there
states = (
    ('string', 'exclusive'),
    ('comment', 'exclusive'),
)

# define literal reserved keywords, these are automatically capitalized and
# added as tokens below, which are returned by `t_ID`
reserved = (
    'extern', 'static',
    'if', 'else',
    'return',
)
reserved_map = dict((word, word.upper()) for word in reserved)

tokens = (
    'LBRACKET', 'RBRACKET',  # []
    'BRACKETS',              # []
    'LBRACE', 'RBRACE',      # {}
    'LPAREN', 'RPAREN',      # ()
    'COMMA', 'SEMICOL',
    'ASSIGN',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO',
    'EQ', 'NE', 'LT', 'GT', 'LE', 'GE',
    'AND', 'OR',
    'NOT', 'INV',
    'TYPE',
    'MODIFY',
    'BOOLCONST', 'CHARCONST', 'INTCONST', 'HEXCONST',
    'STRINGCONST',
    'DOTS',
    'ID',
) + tuple(reserved_map.values())

# change the token type for type keywords and boolean constants, by default
# these would be lexed as identifiers by `t_ID` below
reserved_map['bool']  = 'TYPE'
reserved_map['char']  = 'TYPE'
reserved_map['int']   = 'TYPE'
reserved_map['void']  = 'TYPE'
reserved_map['true']  = 'BOOLCONST'
reserved_map['false'] = 'BOOLCONST'

# regular expressions for tokens that need no special handling logic
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
t_BRACKETS  = r'\[\]'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_COMMA     = r','
t_SEMICOL   = r';'
t_ASSIGN    = r'='
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_MODULO    = r'%'
t_EQ        = r'=='
t_NE        = r'!='
t_LT        = r'<'
t_GT        = r'>'
t_LE        = r'<='
t_GE        = r'>='
t_AND       = r'&&'
t_OR        = r'\|\|'
t_NOT       = r'!'
t_INV       = r'~'
t_DOTS      = r'\.\.\.'
t_MODIFY    = r'(\+|-|\*|/|%|\|\||&&|&|\||\^|<<|>>)='

t_ignore = ' \t'            # ignore whitespace
t_ignore_COMMENT = r'//.*'  # single-line comment

t_string_ignore = ''        # don't ignore characters in string constants
t_comment_ignore = ''       # ... or anything particular in comments


#
# The functions below handle tokens that need special processing to set the
# token type or value.
#


def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    t.type = reserved_map.get(t.value, 'ID')
    return t


def t_number(t):
    r'0x[a-fA-F0-9]+|\d+'
    if t.value.startswith('0x'):
        t.type = 'HEXCONST'     # e.g. 0xabc123
    elif t.value.isdigit():
        t.type = 'INTCONST'     # e.g. 123
    return t


# enter the 'string' state when a " is encountered
def t_string(t):
    r'"'
    t.lexer.string_start = t.lexer.lexpos
    t.lexer.string_buf = ''
    t.lexer.string_escape = False
    t.lexer.in_charconst = False
    t.lexer.begin('string')


# reuse the 'string' state for character constants (enclosed in ') to allow for
# the same charater escaping
def t_char(t):
    r'\''
    t.lexer.string_start = t.lexer.lexpos
    t.lexer.string_buf = ''
    t.lexer.string_escape = False
    t.lexer.in_charconst = True
    t.lexer.begin('string')


# get escape sequences from `ast.StringConst`
reverse_trans = dict((v[-1], chr(k)) for k, v in StringConst.trans.items())


# in the 'string' state, handle escape sequences and maintain a buffer until the
# closing quote is found, then produce a STRINGCONST or CHARCONST token with the
# buffer as its value
def t_string_char(t):
    r'.'
    if t.lexer.string_escape:
        if t.value in reverse_trans:
            # known escape character
            t.lexer.string_buf += reverse_trans[t.value]
        elif t.value.isdigit():
            # octal
            raise NotImplementedError('octal strings are not supported')
        elif t.value == 'x':
            # hex
            raise NotImplementedError('hexadecimal strings are not supported')
        else:
            # unknown escape character, just ignore it
            t.lexer.string_buf += t.value

        t.lexer.string_escape = False
    elif t.value == '\\':
        t.lexer.string_escape = True
    elif not t.lexer.in_charconst and t.value == '"':
        t.lexpos = t.lexer.string_start
        t.value = t.lexer.string_buf
        t.type = 'STRINGCONST'
        t.lexer.begin('INITIAL')
        return t
    elif t.lexer.in_charconst and t.value == '\'':
        assert len(t.lexer.string_buf) == 1
        t.lexpos = t.lexer.string_start
        t.value = t.lexer.string_buf
        t.type = 'CHARCONST'
        t.lexer.begin('INITIAL')
        return t
    elif t.lexer.in_charconst and len(t.lexer.string_buf) > 0:
        raise token_error(t, 'Unexpected %s, expected \'' % t.value[0])
    else:
        t.lexer.string_buf += t.value


def t_string_error(t):
    t_error(t)


def t_comment(t):
    r'/\*'
    t.lexer.begin('comment')


def t_comment_end(t):
    r'\*/|.'
    if t.value == '*/':
        t.lexer.begin('INITIAL')


def t_comment_error(t):
    t_error(t)


def t_ANY_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.lexer.last_newline_pos = t.lexpos + len(t.value) - 1


# The C preprocessor inserts so called 'line markers' into the output.  These
# markers have the following form:
#
#   # <linenum> <filename> <flags>
#
# This marker indicates that all lines after this marker up to the next marker
# come from the file <filename> starting at line <linenum>. After the file name
# can be zero or more flags, these flags are numbered 1-4 and can be ignored.
def t_cpp_line_marker(t):
    r'\#\s\d+\s"[^"]*"(\s[1-4])*'
    groups = t.value.split()
    t.lexer.fname = groups[2][1:-1]
    t.lexer.lineno = int(groups[1]) - 1


def t_error(t):
    raise token_error(t, 'Unexpected \'%s\'' % t.value[0])


# show a lexing error as a `LocationError`, with nice source line highlighting
def token_error(t, message):
    line = t.lexer.lineno
    col = t.lexpos - t.lexer.last_newline_pos
    return LocationError((t.lexer.fname, line, col, line, col), message)


def create_lexer(fname, **kwargs):
    lexer = lex.lex(**kwargs)
    lexer.lineno = 1
    lexer.last_newline_pos = -1
    lexer.fname = fname
    return lexer


if __name__ == '__main__':
    import sys
    lexer = create_lexer('<stdin>')
    src = sys.stdin.read()
    lexer.input(src)

    try:
        tok = lexer.token()
        while tok:
            print(tok)
            tok = lexer.token()
    except LocationError as e:
        e.print(True, src)
