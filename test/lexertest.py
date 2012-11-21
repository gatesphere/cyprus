## cyprus
## lexer test
## PeckJ 20121120
##

import sys
sys.path.append('..')
import lexer as lex

if __name__ == '__main__':
  ts = lex.tokenizefile('test.cyp')
  for t in ts: print t
