## cyprus
## lexer
## PeckJ 20121120
##

import re, fileinput

tokens = [
  'KW_EXISTS',
  'KW_REACTION',
  'KW_AS',
  'KW_PRIORITY',
  'KW_PROBABILITY',
  'IDENTIFIER',
  'OP_PRIORITY_MAXIMAL',
  'OP_PRIORITY_PROBIBILITY',
  'OP_TILDE',
  'OP_PRODUCTION',
  'OP_DISSOLVE',
  'OP_OSMOSE',
  'MOD_CATALYST',
  'MOD_CHARGE_POSITIVE',
  'MOD_CHARGE_NEGATIVE',
  'LEFT_BRACKET',
  'RIGHT_BRACKET',
  'LEFT_PARENTHESIS',
  'RIGHT_PARENTHESIS'
]
  
class Token(object):
  def __init__(self, type, string, start=(0, 0), end=(0, 0), 
      line='', linenum=0, filename=''):
    self.type = type
    self.string = string
    self.start = start
    self.end = end
    self.line = line
    self.linenum = linenum
    self.filename = filename
  
  def __eq__(self, other):
    return (self.type, self.string) == (other.type, other.string)

  def __str__(self):
    return "Token(%s, '%s', %s, %s, '%s', %s, %s)" % (
      self.type, self.string, self.start, self.end,
      self.line, self.linenum, self.filename)

## lex
def lexer(f):
  linenum = 1
  tokens = []
  
  def lexline(line, linenum, f):
    ## stub
    n = 0
    while n < 1:
      yield Token('KW_EXISTS', line, line=line, linenum=linenum)
      n += 1
  
  for line in open(f, 'r'):
    tokens.extend(lexline(line, linenum, f))
    linenum += 1
  return tokens
  

if __name__ == '__main__':
  ts = lexer('test.cyp')
  for t in ts: print t
