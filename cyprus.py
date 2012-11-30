## cyprus
## language logic and runner
## PeckJ 20121126
##

import cyprus_parser as parser
import cyprus_lexer as lexer
from funcparserlib.parser import NoParseError
from funcparserlib.lexer import Token
import sys, getopt

class CyprusClock(object):
  def __init__(self, envs):
    self._tick = 0
    self.envs = envs
  
  def printstatus(self):
    for e in self.envs: e.printstatus()
  
  def tick(self):
    self._tick += 1
    for e in self.envs:
      e.tick()

class CyprusEnvironment(object):
  def __init__(self, name=None, parent=None, contents=[], membranes=[], rules=[]):
    self.name = name
    self.parent = parent
    self.contents = contents
    self.membranes = membranes
    self.staging_area = []
    self.rules = rules
    self.setparents()
    self.setpriorities()

  def printstatus(self, depth=0):
    spaces = " " * (depth * 2)
    print '%s[name: %s' % (spaces, self.name)
    print '%s symbols: %s' % (spaces, self.contents)
    print '%s Membranes:' % spaces
    for m in self.membranes:
      m.printstatus(depth + 1)
    print '%s]' % spaces
  
  def tick(self):
    for m in self.membranes: m.stage1()
    for m in self.membranes: m.stage2()
    self.contents.extend(self.staging_area)
    self.staging_area = []
  
  def setpriorities(self):
    pass # placeholder
  
  def setparents(self):
    for m in self.membranes: m.parent = self
  
  def dissolve(self):
    pass # environments cannot dissolve

  def stage1(self):
    pass # placeholder
  
  def stage2(self):
    pass # placeholder

class CyprusMembrane(CyprusEnvironment):
  def dissolve(self):
    parent.contents.extend(self.contents)
    parent.membranes.remove(self)
  
  def printstatus(self, depth=0):
    spaces = " " * (depth * 4)
    print '%s(name: %s' % (spaces, self.name)
    print '%s symbols: %s' % (spaces, self.contents)
    print '%s Membranes:' % spaces
    for m in self.membranes:
      m.printstatus(depth + 1)
    print '%s)' % spaces
  
class CyprusParticle(object):
  def __init__(self, name, charge=''):
    self.name = name
    self.charge = charge
    
  def __str__(self):
    return "%s%s" % (self.name, self.charge)
  
  def __eq__(self, other):
    return (self.name, self.charge) == (other.name, other.charge)
  
class CyprusRule(object):
  pass

class CyprusProgram(object):
  def __init__(self, tree):
    self.tree = tree
    envs = self.objectify()
    self.clock = CyprusClock(envs)
  
  def objectify(self):
    out = []
    for e in self.tree.kids:
      env = self.buildenvironment(e)
      out.append(env)
    return out
    
  def buildenvironment(self, e, parent=None):
    name = None
    contents = []
    membranes = []
    rules = []
    stmts = []
    for x in e.kids:
      if isinstance(x, Token):
        name = x.value
      if isinstance(x, parser.Statement):
        stmts.append(self.executestatement(x))
    stmts = parser.flatten(stmts)
    print stmts
    for x in stmts:
      if isinstance(x, CyprusMembrane):
        print "MEMBRANE!"
        membranes.append(x)
      if isinstance(x, CyprusRule):
        rules.append(x)
      if isinstance(x, CyprusParticle):
        contents.append(x)
    return CyprusEnvironment(name, parent, contents, membranes, rules)
  
  def executestatement(self, stmt):
    for x in stmt.kids:
      if isinstance(x, parser.Membrane):
        return self.buildmembrane(x)
      
  def buildmembrane(self, membranee):
    return CyprusMembrane()
  
  def run(self):
    self.clock.printstatus()
    while True:
      self.clock.tick()
      self.clock.printstatus()
      x = raw_input()


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
