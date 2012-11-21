## cyprus
## parser
## PeckJ 20121121
##

import lexer
from funcparserlib.parser import (some, a, maybe, many, finished, skip, 
  forward_decl, oneplus, NoParseError)
from funcparserlib.util import pretty_tree

## grammar
##
## program        := {env}, end
## env            := "[", body, "]"
## membrane       := "(", body, ")"
## body           := <name>, {statement}
## statement      := membrane | expr
## expr           := exists | reaction | priority
## exists         := "exists", "~", {name}
## reaction       := reaction_named | reaction_anon
## reaction_anon  := "reaction", "~", name, {name}, "::", {symbol}
## reaction_named := "reaction", "as", name, "~", name, {name} "::", {symbol}
## priority       := priority_max | priority_prob
## priority_max   := "priority", "~", name, ">>", name
## priority_prob  := "priority", "~", name, ">", name, "probability", number
## name           := number | atom
## atom           := [A-Za-z], {[A-Za-z0-9]}
## number         := [0-9], {[0-9]} | {[0-9]}, ".", [0-9], {[0-9]}
## symbol         := atom | "!", name, <"!!", name> | "$", [name]
