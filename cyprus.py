## cyprus
## language logic and runner
## PeckJ 20121126
##

import cyprus_parser as parser
import cyprus_lexer as lexer
from funcparserlib.parser import NoParseError
from funcparserlib.lexer import Token
import sys, getopt

cyprus_rule_lookup_table = {}

class CyprusClock(object):
  def __init__(self, envs):
    self._tick = 0
    self.envs = envs
  
  def printstatus(self):
    print "Clock tick: %s" % self._tick
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
    print '%s rules: %s' % (spaces, self.rules)
    print '%s Membranes:' % spaces
    for m in self.membranes:
      m.printstatus(depth + 1)
    print '%s]' % spaces
  
  def tick(self):
    self.stage1()
    self.stage2()
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
    print '%s rules: %s' % (spaces, self.rules)
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
  
  def __repr__(self):
    return self.__str__()
  
  def __eq__(self, other):
    return (self.name, self.charge) == (other.name, other.charge)
  
class CyprusRule(object):
  def __init__(self, name, req, out, pri=1):
    self.name = name
    self.requirements = req
    self.output = out
    self.priority = pri
  
  def __str__(self):
    if self.name != None:
      return "%s -> %s (%s)[%s])" % (self.requirements, self.output, self.priority, self.name)
    else:
      return "%s -> %s (%s)" % (self.requirements, self.output, self.priority)
  
  def __repr__(self):
    return self.__str__()

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
  
  def buildcontainer(self, e):
    name = None
    parent = None
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
    for x in stmts:
      if isinstance(x, CyprusMembrane):
        membranes.append(x)
      if isinstance(x, CyprusRule):
        rules.append(x)
      if isinstance(x, CyprusParticle):
        contents.append(x)
    return [name, parent, contents, membranes, rules]
  
  def buildenvironment(self, e):
    name, parent, contents, membranes, rules = self.buildcontainer(e)
    return CyprusEnvironment(name, parent, contents, membranes, rules)
  
  def buildmembrane(self, e):
    name, parent, contents, membranes, rules = self.buildcontainer(e)
    return CyprusMembrane(name, parent, contents, membranes, rules)
  
  def executestatement(self, stmt):
    x = stmt.kids[0]
    if isinstance(x, parser.Membrane):
      return self.buildmembrane(x)
    elif isinstance(x, parser.Token):
      if x.type == 'kw_exists':
        return self.buildparticles(stmt)
      elif x.type == 'kw_reaction':
        return self.buildrule(stmt)
      elif x.type == 'kw_priority':
        self.setpriority(stmt)
        return None
      else:
        print "ERROR: %s" % stmt
    else:
      print "ERROR: %s" % stmt
  
  def buildparticles(self, stmt):
    particles = stmt.kids[2:]
    out = []
    for p in particles:
      out.append(CyprusParticle(p.value))
    return out
    
  def buildrule(self, stmt):
    name = None
    req = []
    out = []
    pri = 1
    particulars = stmt.kids[1:]
    if particulars[0] is None:
      particulars = particulars [2:]
    else:
      name = particulars[1].value
      particulars = particulars[3:]
    prod = False
    dissolve = False
    osmose = False
    osmosename = False
    osmoselocation = False
    for x in particulars:
      if x: ## error...
        if x.type == 'op_production':
          prod = True
          continue
        elif x.type == 'op_dissolve':
          dissolve = True
          continue
        elif x.type == 'op_osmose':
          osmose = True
          continue
      if dissolve:
        if not x:
          particle = CyprusParticle("$")
        else:
          particle = CyprusParticle("$%s" % x.value)
        dissolve = False
      elif osmose:
        if not osmosename:
          osmosename = x.value
          continue
        if osmosename:
          if not x:
            particle = CyprusParticle("!%s" % osmosename)
            osmose, osmosename, osmoselocation = False, False, False
          elif x.type == 'op_osmose_location':
            continue
          else:
            osmoselocation = x.value
            particle = CyprusParticle("!%s!!%s" % (osmosename, osmoselocation))
            osmose, osmosename, osmoselocation = False, False, False
      else:
        particle = CyprusParticle(x.value)
      if prod: out.append(particle)
      else: req.append(particle)
    rule = CyprusRule(name, req, out, pri)
    if name:
      cyprus_rule_lookup_table[name] = rule
    return rule
        
  def setpriority(self, stmt):
    greater, lesser = stmt.kids[2].value, stmt.kids[4].value
    greater = cyprus_rule_lookup_table[greater]
    lesser = cyprus_rule_lookup_table[lesser]
    if greater.priority <= lesser.priority:
      greater.priority += 1
  
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
