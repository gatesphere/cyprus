from random import shuffle

class Environment(object):
  def __init__(self):
    self.symbols = []
    self.membranes = []
    self.staging_area = []  

  def print_status(self):
    print "symbols: %s" % self.symbols
    print "membranes: %s" % self.membranes

  def print_world(self):
    print "-----------------------"
    self.print_status()
    print
    for m in self.membranes:
      m.print_status()
      print
  
  def tick(self):
    for m in self.membranes: m.stage1()
    for m in self.membranes: m.stage2()
    self.symbols.extend(self.staging_area)
    self.staging_area = []

class Membrane(object):
  def __init__(self):
    self.symbols = []
    self.membranes = []
    self.rules = []
    self.parent = None
    self.staging_area = []

  def print_status(self):
    for m in self.membranes: m.print_status()
    print "symbols: %s" % self.symbols
    print "membranes: %s" % self.membranes
    print "parent: %s" % self.parent
    print "staging_area: %s" % self.staging_area
  
  def rule_is_applicable(self, rule):
    counts = [(s, rule.requirements.count(s)) for s in rule.requirements]
    s_counts = dict([(s, self.symbols.count(s)) for s in self.symbols])
    for (s, c) in counts:
      if s_counts.get(s, None) == None or s_counts[s] < c: return False
    return True
  
  def apply_rule(self, rule):
    if self.rule_is_applicable(rule):
      for s in rule.requirements: self.symbols.remove(s)
    self.staging_area.extend(rule.output)
  
  def dissolve(self):
    self.parent.symbols.extend(self.symbols)
    self.symbols = []
    for m in self.membranes:
      m.parent = self.parent
      self.parent.membranes.append(m)
    self.parent.membranes.remove(self)

  def stage1(self):
    for m in self.membranes: m.stage1()
    rule_ranks = {}
    for rule in self.rules:
      r = rule_ranks.get(rule.priority, [])
      r.append(rule)
      rule_ranks[rule.priority] = r
      print '%s' % rule
    for p in sorted(rule_ranks.keys(), reverse=True):
      rs = rule_ranks[p]
      shuffle(rs)
      for rule in rs:
        while self.rule_is_applicable(rule):
          self.apply_rule(rule)
  
  def stage2(self):
    for m in self.membranes: m.stage2()
    self.symbols.extend(self.staging_area)
    self.staging_area = []
    print self.symbols
    if DeltaSymbol in self.symbols:
      self.symbols.remove(DeltaSymbol)
      self.dissolve()

class Rule(object):
  def __init__(self, req, out, pri):
    self.requirements = req
    self.output = out
    self.priority = pri
  
  def __str__(self):
    return '(%s, %s)' % (self.requirements, self.output)

DeltaSymbol = 'delta'

## example problem: generate square numbers
membrane_3 = Membrane()
membrane_3.symbols = ['a', 'c']
membrane_3.rules = [Rule(['a'], ['a', 'b'], 1),
                    Rule(['a'], ['b', DeltaSymbol], 1),
                    Rule(['c'], ['c', 'c'], 1)]

membrane_2 = Membrane()
membrane_2.rules = [Rule(['b'], ['d'], 1),
                    Rule(['d'], ['d', 'e'], 1),
                    Rule(['c', 'c'], ['c'], 2),
                    Rule(['c'], [DeltaSymbol], 1)]
membrane_2.membranes.append(membrane_3)
membrane_3.parent = membrane_2

membrane_1 = Membrane()
membrane_1.rules = [Rule(['e'], ['e', DeltaSymbol], 1)]
membrane_1.membranes.append(membrane_2)
membrane_2.parent = membrane_1

env = Environment()
env.membranes.append(membrane_1)
membrane_1.parent = env

if __name__ == '__main__':
  while True:
    env.print_world()
    raw_input("<ENTER>")
    env.tick()
