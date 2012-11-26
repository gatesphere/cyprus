## cyprus
## language logic and runner
## PeckJ 20121126
##

import cyprus_parser as parser
import cyprus_lexer as lexer
from funcparserlib.parser import NoParseError
import sys, getopt

class CyprusClock(object):
  def __init__(self, envs):
    self._tick = 0
    self.envs = envs
    
  def tick():
    self._tick += 1
    for e in self.envs:
      e.tick()

class CyprusEnvironment(object):
  def __init__(self, name, parent, contents, membranes, rules):
    self.name = name
    self.parent = parent
    self.contents = contents
    self.membranes = membranes
    self.rules = rules
    setpriorities()
    
  def setpriorities(self):
    pass # placeholder
  
  def dissolve(self):
    pass # environments cannot dissolve

class CyprusMembrane(CyprusEnvironment):
  def dissolve(self):
    parent.contents.extend(self.contents)
    parent.membranes.remove(self)

class CyprusPriority(object):
  def __init__(self, rule1, rule2, priority):
    self.rule1 = rule1
    self.rule2 = rule2
    self.priority = priority
  
  def isMaximal(self):
    return self.priority == 1.0
  
class CyprusParticle(object):
  def __init__(self, name, parent, charge=''):
    self.name = name
    self.parent = parent
    self.charge = charge
    
  def __str__(self):
    return "%s%s" % (self.name, self.charge)
  
  def __eq__(self, other):
    return (self.name, self.charge) == (other.name, other.charge)
  
class CyprusRule(object):
  pass

class CyprusProgram(object):
  def __init__(self, tree):
    self.clock = CyprusClock(None)  ## placeholder
    self.tree = tree
    
  def run(self):
    pass

def usage():
  print "usage: python cyprus.py [-p] <filename.cyp>"
  print "       python cyprus.py -v"
  print "       python cyprus.py -h"
  print "  -p: pretty-print a parse tree and exit"
  print "  -v: display version info and exit"
  print "  -h: display this help text and exit"
  
def version():
  print "cyprus version 20121126"
  print "Jacob Peck (suspended-chord)"
  print "http://github.com/gatesphere/cyprus"

if __name__ == '__main__':
  args = sys.argv[1:]
  try:
    opts, args = getopt.getopt(args, 'pvh')
  except:
    usage()
    sys.exit()
  ptree, pversion, phelp = False, False, False
  for opt, a in opts:
    if   opt == '-p': ptree = True
    elif opt == '-v': pversion = True
    elif opt == '-h': phelp = True
  if pversion:
    version()
    sys.exit()
  if len(args) != 1 or phelp:
    usage()
    sys.exit()
  
  filename = args[0]
  
  if ptree:
    try:
      print parser.ptree(parser.parse(lexer.tokenizefile(filename)))
    except NoParseError as e:
      print "Could not parse file:"
      print e.msg
    sys.exit()
  
  ## actual logic
  try:
    tree = parser.parse(lexer.tokenizefile(filename))
  except NoParseError as e:
    print "Could not parse file:"
    print e.msg
    sys.exit()
  tree = CyprusProgram(tree)
  tree.run()
  
  sys.exit()
