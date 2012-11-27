## cyprus
## lexer
## PeckJ 20121121
##

from funcparserlib.lexer import make_tokenizer, Token, LexerError

ENCODING = 'utf-8'

def tokenize(str):
  'str -> Sequence(Token)'
  specs = [
    ('comment',                 (r'//.*',)),
    ('newline',                 (r'[\r\n]+',)),
    ('space',                   (r'[ \t\r\n]+',)),
    ('kw_exists',               (r'exists',)),
    ('kw_reaction',             (r'reaction',)),
    ('kw_as',                   (r'as',)),
    ('kw_priority',             (r'priority',)),
    ('op_priority_maximal',     (r'>>',)),
    ('op_tilde',                (r'~',)),
    ('op_production',           (r'::',)),
    ('op_dissolve',             (r'\$',)),
    ('op_osmose_location',      (r'!!',)),
    ('op_osmose',               (r'!',)),
    ('mod_catalyst',            (r'\*',)),
    ('mod_charge_positive',     (r'\+',)),
    ('mod_charge_negative',     (r'-',)),
    ('env_open',                (r'\[',)),
    ('env_close',               (r'\]',)),
    ('membrane_open',           (r'\(',)),
    ('membrane_close',          (r'\)',)),
    ('number',                  (r'-?(\.[0-9]+)|([0-9]+(\.[0-9]*)?)',)),
    ('name',                    (r'[A-Za-z\200-\377_][A-Za-z\200-\377_0-9]*',))
  ]
  useless = ['comment', 'space', 'newline']
  t = make_tokenizer(specs)
  return [x for x in t(str) if x.type not in useless]

def tokenizefile(f):
  return tokenize(open(f, 'r').read())
