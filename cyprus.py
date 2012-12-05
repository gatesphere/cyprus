## cyprus
## language logic and runner
## PeckJ 20121204
##

# python stdlib
import cyprus_parser as parser
import cyprus_lexer as lexer
import sys, getopt
from random import shuffle

# cyprus stuff
from funcparserlib.parser import NoParseError
from funcparserlib.lexer import Token

# global state
cyprus_version = 20121205
cyprus_rule_lookup_table = {}
cyprus_membrane_lookup_table = {}
cyprus_state_rule_applied = True

# the clock, governs the system's operation
class CyprusClock(object):
  def __init__(self, envs):
    self._tick = 0
    self.envs = envs
  
  def printstatus(self):
    print "Clock tick: %s" % self._tick
    for e in self.envs: e.printstatus()
  
  def printfinalcontents(self):
    for e in self.envs:
      if e.name:
        print "%s: %s" % (e.name, e.contents)
      else:
        print "Unnamed env %d: %s" % (self.envs.index(e), e.contents)
  
  def tick(self):
    self._tick += 1
    for e in self.envs:
      e.tick()

# An environment - a container object for rules and particles
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
    print '%s staging area: %s' % (spaces, self.staging_area)
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
    self.ruleranks = {}
    for rule in self.rules:
      r = self.ruleranks.get(rule.priority, [])
      r.append(rule)
      self.ruleranks[rule.priority] = r
  
  def setparents(self):
    for m in self.membranes: m.parent = self
  
  def dissolve(self):
    pass # environments cannot dissolve

  def rule_is_applicable(self, rule):
    counts = set([(s.__str__(), rule.requirements.count(s)) for s in rule.requirements])
    s_counts = dict([(s.__str__(), self.contents.count(s)) for s in self.contents])
    for (s, c) in counts:
      if s_counts.get(s, None) == None or s_counts[s] < c: return False
    return True
    
  def apply_rule(self, rule):
    global cyprus_state_rule_applied
    if self.rule_is_applicable(rule):
      cyprus_state_rule_applied = True
      for s in rule.requirements: self.contents.remove(s)
    self.staging_area.extend(rule.output)

  ## apply all rules maximally, non-deterministically
  def stage1(self):
    for m in self.membranes: m.stage1()
    for p in sorted(self.ruleranks.keys(), reverse=True):
      rs = self.ruleranks[p]
      shuffle(rs)
      for rule in rs:
        while self.rule_is_applicable(rule):
          self.apply_rule(rule)
  
  ## apply changes from stage 1, including dissolutions and osmosis
  def stage2(self):
    global cyprus_membrane_lookup_table
    for m in self.membranes: m.stage2()
    self.contents.extend(self.staging_area)
    self.staging_area = []
    contentcopy = list(self.contents)
    for s in contentcopy:
      if isinstance(s, CyprusDissolveParticle):
        self.contents.remove(s)
        if s.target:
          if not cyprus_membrane_lookup_table.get(s.target, None):
            msg = "ERROR: No containers defined with name '%s'" % s.target
            raise CyprusException(msg)
          cyprus_membrane_lookup_table[s.target].dissolve()
        else:
          self.dissolve()
          break
      if isinstance(s, CyprusOsmoseParticle):
        self.contents.remove(s)
        if s.target:
          if not cyprus_membrane_lookup_table.get(s.target, None):
            msg = "ERROR: No containers defined with name '%s'" % s.target
            raise CyprusException(msg)
          cyprus_membrane_lookup_table[s.target].contents.append(
            CyprusParticle(s.payload))
        elif self.parent:
          self.parent.contents.append(CyprusParticle(s.payload))
        else: # environments cannot be osmosed through
          self.contents.append(s)

class CyprusMembrane(CyprusEnvironment):
  def dissolve(self):
    self.parent.contents.extend(self.contents)
    self.parent.membranes.remove(self)
    self.parent.membranes.extend(self.membranes)
    self.contents = []
    self.staging_area = []
    self.rules = []
    if self.name:
      del(cyprus_membrane_lookup_table[self.name])
  
  def printstatus(self, depth=0):
    spaces = " " * (depth * 4)
    print '%s(name: %s' % (spaces, self.name)
    print '%s symbols: %s' % (spaces, self.contents)
    print '%s rules: %s' % (spaces, self.rules)
    print '%s staging area: %s' % (spaces, self.staging_area)
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

class CyprusDissolveParticle(CyprusParticle):
  def __init__(self, target=None):
    self.target = target
    
  def __str__(self):
    if self.target:
     return "$%s" % self.target
    else:
      return "$"
  
  def __eq__(self, other):
    if isinstance(other, CyprusDissolveParticle):
      return other.target == self.target
    else:
      return False

class CyprusOsmoseParticle(CyprusParticle):
  def __init__(self, payload, target=None):
    self.payload = payload
    self.target = target
    
  def __str__(self):
    if self.target:
      return "!%s!!%s" % (self.payload, self.target)
    else:
      return "!%s" % self.payload
  
  def __eq__(self, other):
    if isinstance(other, CyprusOsmoseParticle):
      return (self.target, self.payload) == (other.target, other.payload)
    else:
      return False

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

class CyprusException(Exception):
  def __init__(self, message):
    self.message = message

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
    global cyprus_membrane_lookup_table
    name, parent, contents, membranes, rules = self.buildcontainer(e)
    env = CyprusEnvironment(name, parent, contents, membranes, rules)
    if name:
      if cyprus_membrane_lookup_table.get(name, None):
        msg = "ERROR: Multiple containers defined with name '%s'" % name
        raise CyprusException(msg)
      cyprus_membrane_lookup_table[name] = env
    return env
  
  def buildmembrane(self, e):
    global cyprus_membrane_lookup_table
    name, parent, contents, membranes, rules = self.buildcontainer(e)
    mem = CyprusMembrane(name, parent, contents, membranes, rules)
    if name:
      if cyprus_membrane_lookup_table.get(name, None):
        msg = "ERROR: Multiple containers defined with name '%s'" % name
        raise CyprusException(msg)
      cyprus_membrane_lookup_table[name] = mem
    return mem
  
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
    global cyprus_rule_lookup_table
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
          particle = CyprusDissolveParticle()
        else:
          particle = CyprusDissolveParticle(x.value)
        dissolve = False
      elif osmose:
        if not osmosename:
          osmosename = x.value
          continue
        if osmosename:
          if not x:
            particle = CyprusOsmoseParticle(osmosename)
            osmose, osmosename, osmoselocation = False, False, False
          elif x.type == 'op_osmose_location':
            continue
          else:
            osmoselocation = x.value
            particle = CyprusOsmoseParticle(osmosename, osmoselocation)
            osmose, osmosename, osmoselocation = False, False, False
      else:
        particle = CyprusParticle(x.value)
      if prod: out.append(particle)
      else: req.append(particle)
    rule = CyprusRule(name, req, out, pri)
    if name:
      if cyprus_rule_lookup_table.get(name, None):
        msg = "ERROR: Multiple reactions defined with name '%s'" % name
        raise CyprusException(msg)
      cyprus_rule_lookup_table[name] = rule
    return rule
        
  def setpriority(self, stmt):
    global cyprus_rule_lookup_table
    greatern, lessern = stmt.kids[2].value, stmt.kids[4].value
    greater = cyprus_rule_lookup_table.get(greatern, None)
    lesser = cyprus_rule_lookup_table.get(lessern, None)
    if not greater:
      msg = "ERROR: No reactions defined with name '%s'" % greatern
      raise CyprusException(msg)
    if not lesser:
      msg = "ERROR: No reactions defined with name '%s'" % lessern
      raise CyprusException(msg)
    if greater.priority <= lesser.priority:
      greater.priority += 1
  
  def run(self, verbose=False):
    global cyprus_state_rule_applied
    if verbose: self.clock.printstatus()
    while cyprus_state_rule_applied:
      cyprus_state_rule_applied = False
      self.clock.tick()
      if verbose: self.clock.printstatus()
    self.clock.printfinalcontents()
      
def usage():
  print "usage: python cyprus.py [-p | -V] <filename.cyp>"
  print "       python cyprus.py -v"
  print "       python cyprus.py -h"
  print "  -p: pretty-print a parse tree and exit"
  print "  -V: display verbose output of the program's execution"
  print "  -v: display version info and exit"
  print "  -h: display this help text and exit"
  
def version():
  global cyprus_version
  print "cyprus version %s" % cyprus_version
  print "Jacob Peck (suspended-chord)"
  print "http://github.com/gatesphere/cyprus"

if __name__ == '__main__':
  args = sys.argv[1:]
  try:
    opts, args = getopt.getopt(args, 'pVvh')
  except:
    usage()
    sys.exit()
  ptree, pversion, phelp, pverbose = False, False, False, False
  for opt, a in opts:
    if   opt == '-p': ptree = True
    elif opt == "-V": pverbose = True
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
  try:
    tree = CyprusProgram(tree)
    tree.run(verbose=pverbose)
  except CyprusException as e:
    print e.message
  
  sys.exit()
