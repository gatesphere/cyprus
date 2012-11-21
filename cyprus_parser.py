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

def flatten(x):
  result = []
  for el in x:
    if hasattr(el, "__iter__") and not isinstance(el, basestring):
      result.extend(flatten(el))
    else:
      result.append(el)
  return result

class Grouping(object):
  def __init__(self, kids):
    try:
      self.kids = list(flatten([kids]))
    except TypeError:
      self.kids = [kids]

class Program(Grouping):
  pass
  
class Environment(Grouping):
  pass
  
class Membrane(Grouping):
  pass


class Statement(Grouping):
  pass

def parse(tokens):
  
  ## building blocks
  kw_priority = some(toktype("kw_priority"))
  kw_probability = some(toktype("kw_probability"))
  kw_reaction = some(toktype("kw_reaction"))
  kw_exists = some(toktype("kw_exists"))
  kw_as = some(toktype("kw_as"))
  op_tilde = some(toktype("op_tilde"))
  op_priority_maximal = some(toktype("op_priority_maximal"))
  op_priority_probability = some(toktype("op_priority_probability"))
  op_production = some(toktype("op_production"))
  atom = some(toktype("name"))
  number = some(toktype("number"))
  dissolve = some(toktype("op_dissolve"))
  osmose = some(toktype("op_osmose"))
  env_open = some(toktype("env_open"))
  env_close = some(toktype("env_close"))
  membrane_open = some(toktype("membrane_open"))
  membrane_close = some(toktype("membrane_close"))
  
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
  
  expr = (exists | reaction | priority)
  
  statement = with_forward_decls(lambda: membrane | expr) >> Statement
  
  body = maybe(name) + many(statement)
  
  membrane = (skip(membrane_open) + body + skip(membrane_close)) >> Membrane
  env = (skip(env_open) + body + skip(env_close)) >> Environment
  
  program = many(env) + skip(finished) >> Program
  
  return program.parse(tokens)
  
def ptree(tree):
  def kids(x):
    if isinstance(x, Grouping):
      return x.kids
    else:
      return []
  def show(x):
    #print "show(%r)" % x
    if isinstance(x, Program):
      return '{Program}'
    elif isinstance(x, Environment):
      return '{Environment}'
    elif isinstance(x, Membrane):
      return '{Membrane}'
    elif isinstance(x, Statement):
      return '{Statement}'
    else:
      return repr(x)
  return pretty_tree(tree, kids, show)
