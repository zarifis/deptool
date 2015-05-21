import json, subprocess, copy, re, time

ua_dict = {
"chrome":       "Chrome-37.0-Win7-64-bit",
"firefox":      "Firefox-32.0-Win7-64-bit",
"ie10":         "IE-10.0-Win",
"ie9":          "IE-9.0-Win",
"opera":        "Opera-12.14-Win",
"safari-ipad":  "Safari-6.0-iPad",
"safari-mac":   "Safari-7.0-MacOSX",
}

def _inv_tree_step(parent, subtree, invTree):
  for child,grandchildren in subtree.iteritems():
    invTree[child] = parent
    if len(grandchildren)>0:
      _inv_tree_step(child, grandchildren, invTree)

def getInverseTree(tree):
  basePage = tree.keys()[0]
  invTree = {}
  _inv_tree_step(basePage, tree[basePage], invTree)
  return invTree

def getInvCriticalTree(depTree):
  invDepTree = getInverseTree(depTree)
  invCriticalTree = {}
  for k,v in invDepTree.iteritems():
    if k in invDepTree.values():
      invCriticalTree[k]=v  
  return invCriticalTree

def mergeTrees(t1, t2):
  """ Merge inversed t2 into t1 """
  t1["xxx"]=None
  for k,v in t2.iteritems():
    if k not in t1:
      t1[k] = v
  del t1["xxx"]
  return t1

def compareTrees(t1, t2):
  if not t1: return
  c1 = c2 = 0
  for child in t2:
    if child not in t1:
      c1 += 1
    else:
      if t1[child] != t2[child]:
        c2 += 1
        print "Parent Changed:"
        print "  Was: ", t1[child], "==>", child
        print "   Is: ", t2[child], "==>", child
  print "(",c1, "children dissapeared,",c2, "children changed parents )"

def loadTree(treefile):
  return json.load(open(treefile))

casper = "casperjs"
script = "resources.js"

def _getResources(url, ua):
  # Download a web page 10 times, return the list of resources that appear in all 10 downloads
  # as well as resources that appeared in some but not all of the downloads.
  resources_runs = []
  for i in range(0,10):
    output = subprocess.Popen([casper, script, url, ua, ""], stdout=subprocess.PIPE).communicate()[0]
    resources = output.split('\n')[0:-1]
    resources_runs.append(set(resources))
  consistent_resources = set.intersection(*resources_runs)
  occasional_resources = set()
  for s in resources_runs:
    occasional_resources.update(s - consistent_resources)
  return consistent_resources, occasional_resources

def get_dep_tree(url, ua):

  if url[-1] != '/': url = url+'/'

  (allResourcesSet, occasionalResourcesSet) = _getResources(url, ua)

  basePageDependencies = copy.copy(allResourcesSet)
  if url in basePageDependencies: basePageDependencies.remove(url)

  criticalResources = []
  for r in allResourcesSet:
    if re.match(r'http:\/\/.*\.css\??.*', r) or re.match(r'http:\/\/.*\.js\??.*', r) or re.match(r'http:\/\/.*\.htm\??.*', r):
      criticalResources.append(r)

  # Collect and organize all descendants
  descendants = {}
  t = {}
  for r in basePageDependencies:
    t[r]=''
  descendants[url]=t

  nonCriticalResources = allResourcesSet - set(criticalResources)
  if url in nonCriticalResources:
    nonCriticalResources.remove(url)
  for r in nonCriticalResources:
    descendants[r] = {}

  """
  print "Finished 1st download."
  print len(allResourcesSet), "total resources"
  print len(criticalResources), "critical resources"
  print len(occasionalResourcesSet), "occasional resources"
  print ''
  """

  cr = sorted(list(criticalResources))
  for i in range(0,len(cr)):
    excluded = cr[i]
    output = subprocess.Popen([casper, script, url, ua, excluded], stdout=subprocess.PIPE).communicate()[0]
    descendants_list = output.split('\n')[0:-1]
    desc = allResourcesSet - set(descendants_list)
    desc.remove(excluded)
    t = {}
    for n in desc:
      t[n]={}
    descendants[excluded]=t

  from operator import itemgetter
  ordered_by_descendants = sorted(descendants, key=lambda k: len(descendants[k]))

  direct_children = {}
  adopted = set()
  for s in ordered_by_descendants:
    dir_children = []
    for r in descendants[s]:
      if r not in adopted:
        dir_children.append(r)
        adopted.add(r)
    direct_children[s] = dir_children

  dep_tree = {url:{}}

  def add_children(key, node):
    if not direct_children[key]:
      return
    for c in direct_children[key]:
      node[c] = {}
      add_children(c, node[c])

  add_children(url, dep_tree[url])

  return dep_tree

