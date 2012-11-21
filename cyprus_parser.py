## cyprus
## parser
## PeckJ 20121121
##

from funcparserlib.parser import (some, a, maybe, many, finished, skip, 
  with_forward_decls, oneplus, NoParseError)
from funcparserlib.lexer import Token
from funcparserlib.util import pretty_tree

## grammar
#
# program        := {env}
# env            := "[", body, "]"
# membrane       := "(", body, ")"
# body           := <name>, {statement}
# statement      := membrane | expr
# expr           := exists | reaction | priority
# exists         := "exists", "~", name, {name}
# reaction       := "reaction", <"as", name>, "~", name, {name}, "::",
#                    {symbol} 
# priority       := priority_max | priority_prob
# priority_max   := "priority", "~", name, ">>", name
# priority_prob  := "priority", "~", name, ">", name, "probability", number
# name           := number | atom
# atom           := [A-Za-z], {[A-Za-z0-9]}
# number         := [0-9], {[0-9]} | {[0-9]}, ".", [0-9], {[0-9]}
# symbol         := atom | "!", name, <"!!", name> | "$", [name]

tokval = lambda tok: tok.value
toktype = lambda type: lambda tok: tok.type == type
make_number = lambda str: float(str)

class Grouping(object):
  def __init__(self, kids):
    self.kids = kids

def parse(tokens):
  
  ## building blocks
  kw_priority = some(toktype("kw_priority")) >> tokval
  kw_probability = some(toktype("kw_probability")) >> tokval
  kw_reaction = some(toktype("kw_reaction")) >> tokval
  kw_exists = some(toktype("kw_exists")) >> tokval
  kw_as = some(toktype("kw_as")) >> tokval
  op_tilde = some(toktype("op_tilde")) >> tokval
  op_priority_maximal = some(toktype("op_priority_maximal")) >> tokval
  op_priority_probability = some(toktype("op_priority_probability")) >> tokval
  op_production = some(toktype("op_production")) >> tokval
  atom = some(toktype("name")) >> tokval
  number = some(toktype("number")) >> tokval
  dissolve = some(toktype("op_dissolve")) >> tokval
  osmose = some(toktype("op_osmose")) >> tokval
  env_open = some(toktype("env_open")) >> tokval
  env_close = some(toktype("env_close")) >> tokval
  membrane_open = some(toktype("membrane_open")) >> tokval
  membrane_close = some(toktype("membrane_close")) >> tokval
  
  ## grammar from the bottom up
  name = atom | number
  symbol = atom | dissolve | osmose
  
  priority_max = kw_priority + op_tilde + name + op_priority_maximal + name
  priority_prob = (kw_priority + op_tilde + name + op_priority_probability + 
                  name + kw_probability + number)
  priority = priority_max | priority_prob
  
  reaction = (kw_reaction + maybe(kw_as + name) + op_tilde + 
             oneplus(name) + op_production + many(symbol))
  
  exists = kw_exists + op_tilde + oneplus(name)
  
  expr = (exists | reaction | priority) >> Grouping
  
  statement = with_forward_decls(lambda: membrane | expr) >> Grouping
  
  body = name + many(statement) >> Grouping
  
  membrane = (membrane_open + body + membrane_close) >> Grouping
  env = (env_open + body + env_close) >> Grouping
  
  program = many(env) + skip(finished)
  
  return program.parse(tokens)
  
def ptree(tree):
  def kids(x):
    if isinstance(x, Grouping):
      return x.kids
    else:
      return []
  def show(x):
    if isinstance(x, Token):
      return x.pformat()
    elif isinstance(x, Grouping):
      return '{}'
    else:
      return repr(x)
  return pretty_tree(tree, kids, show)
