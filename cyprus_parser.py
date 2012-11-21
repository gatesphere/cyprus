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
make_number = lambda str: float(str)

class Grouping(object):
  def __init__(self, kids):
    self.kids = kids

def parse(tokens):
  
  ## building blocks
  kw_priority = some(lambda tok: tok.type =="kw_priority") >> tokval
  kw_probability = some(lambda tok: tok.type == "kw_probability") >> tokval
  kw_reaction = some(lambda tok: tok.type == "kw_reaction") >> tokval
  kw_exists = some(lambda tok: tok.type == "kw_exists") >> tokval
  kw_as = some(lambda tok: tok.type == "kw_as") >> tokval
  op_tilde = some(lambda tok: tok.type == "op_tilde") >> tokval
  op_priority_maximal = some(lambda tok: tok.type == "op_priority_maximal") >> tokval
  op_priority_probability = some(lambda tok: tok.type == "op_priority_probability") >> tokval
  op_production = some(lambda tok: tok.type == "op_production") >> tokval
  atom = some(lambda tok: tok.type == "name") >> tokval
  number = some(lambda tok: tok.type == "number") >> tokval >> make_number
  dissolve = some(lambda tok: tok.type == "op_dissolve") >> tokval
  osmose = some(lambda tok: tok.type == "op_osmose") >> tokval
  env_open = some(lambda tok: tok.type == "env_open") >> tokval
  env_close = some(lambda tok: tok.type == "env_close") >> tokval
  membrane_open = some(lambda tok: tok.type == "membrane_open") >> tokval
  membrane_close = some(lambda tok: tok.type == "membrane_close") >> tokval
  
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
