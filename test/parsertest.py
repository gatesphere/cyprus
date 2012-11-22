## cyprus
## parser test
## PeckJ 20121120
##

import sys
sys.path.append('..')
import cyprus_parser as parser
import cyprus_lexer as lexer
from funcparserlib.parser import NoParseError

if __name__ == '__main__':
  try:
    tree = parser.parse(lexer.tokenizefile('test.cyp'))  
    print parser.ptree(tree)
  except NoParseError as e:
    print e
