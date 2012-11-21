## cyprus
## lexer test
## PeckJ 20121120
##

import sys
sys.path.append('..')
import cyprus_lexer as lexer

if __name__ == '__main__':
  ts = lexer.tokenizefile('test.cyp')
  for t in ts: print t
