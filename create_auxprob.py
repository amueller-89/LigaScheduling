from pyscipopt import Model, quicksum
import sys

orig = Model("orig")
sym  = Model("sym")

# read instance
orig.readProblem(sys.argv[1])
print("read problem", orig.getProbName())
orig_vars = orig.getVars()
orig_conss = orig.getConss()

if orig.getNConss() > 10000 or orig.getNVars() > 10000:
  print("instance too large")
  exit(0)

# create problem to detect symmetries
sym_vars = [sym.addVar(name=v.name + "$", vtype="BINARY", lb=0, ub=1, obj=1) for v in orig_vars]
varmap = {orig_vars[k].name : sym_vars[k] for k in range(len(orig_vars))}
idxmap = {orig_vars[k].name : k for k in range(len(orig_vars))}
bdmap = {orig_vars[k].name : orig_vars[k].getLbGlobal() + orig_vars[k].getUbGlobal() for k in range(len(orig_vars))}

for k in range(len(orig_vars)):
  if orig.isInfinity(-orig_vars[k].getLbGlobal()) or orig.isInfinity(orig_vars[k].getUbGlobal()):
    bdmap[orig_vars[k].name] = 0.0

    if orig.isInfinity(-orig_vars[k].getLbGlobal()) != orig.isInfinity(orig_vars[k].getUbGlobal()):
      sym.addCons(varmap[orig_vars[k].name] == 0)

# add constraints for non-zeros in objective function
for v in orig_vars:
  if v.getObj() != 0:
    sym.addCons(varmap[v.name] == 0)

for c in orig_conss:
  bilinterms = []
  quadterms = []
  linterms = []

  if c.isLinear():
    tmp = orig.getValsLinear(c)
    linterms = [(v, tmp[v.name]) for v in orig_vars if v.name in tmp]
  elif c.isQuadratic():
    bilinterms, quadterms, linterms = orig.getTermsQuadratic(c)
  else:
    print(c, "unknown constraint type -> exit")
    exit(0)

  # add z_i - z_j constraints
  for (v,w,a) in bilinterms:
      sym.addCons(varmap[v.name] - varmap[w.name] == 0)

  # add h_k constraint
  sym.addCons(quicksum(a * bdmap[v.name] * varmap[v.name] for (v,a) in linterms)
              + quicksum(b * bdmap[v.name] * varmap[v.name] + a * bdmap[v.name] * bdmap[v.name] * varmap[v.name] * varmap[v.name] for (v,a,b) in quadterms)
              + quicksum(a * bdmap[v.name] * bdmap[w.name] * varmap[v.name] * varmap[w.name] for (v,w,a) in bilinterms) == 0)
		
  # add g_k constraints
  sum = [0 for col in range(len(orig_vars))]
  found = [False for col in range(len(orig_vars))]

  for (v,a) in linterms:
    sum[idxmap[v.name]] -= a * varmap[v.name]
    found[idxmap[v.name]] = True

  for (v,w,a) in bilinterms:
    sum[idxmap[v.name]] += a * bdmap[w.name] * varmap[w.name] * (1 - 2 * varmap[v.name])
    sum[idxmap[w.name]] += a * bdmap[v.name] * varmap[v.name] * (1 - 2 * varmap[w.name])
    found[idxmap[v.name]] = True
    found[idxmap[w.name]] = True

  for (v,a,b) in quadterms:
    sum[idxmap[v.name]] += -b * varmap[v.name] + 2 * a * bdmap[v.name] * varmap[v.name] * (1 - 2 * varmap[v.name])
    found[idxmap[v.name]] = True

  for v in orig_vars:
    if found[idxmap[v.name]]:
      sym.addCons(sum[idxmap[v.name]] == 0)

sym.setMaximize()

sym.writeProblem(sys.argv[2] + orig.getProbName() + "_aux.cip")

print("solving problem")
sym.optimize()
print("problem solved")

sol = sym.getBestSol()
solval = sym.getSolObjVal(sol)

#
# build partition depending on bilinear terms
#
    

if solval != 0:
  terms = set()
  aff_vars = []
  
  for k in range(len(sym_vars)):
    if sym.getSolVal(sol, sym_vars[k]) != 0:
      aff_vars.append(k)

  for c in orig_conss:
    if c.isQuadratic():
      bilinterms, quadterms, linterms = orig.getTermsQuadratic(c)
      for (v,w,a) in bilinterms:
        terms.add((v.name,w.name))

  #
  # modify auxproblem according to partition
  #

  for k in aff_vars:
    v = orig_vars[k]
    orig.chgVarUb(v, bdmap[v.name] * 0.5)
    aff_vars.remove(k)
    for l in aff_vars:
      w = orig_vars[l]
      if (v.name,w.name) in terms:
        aff_vars.remove(l)

  orig.writeProblem(sys.argv[3] + orig.getProbName() + ".cip")
