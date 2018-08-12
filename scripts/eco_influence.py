


# laslo karolyi <laszlo@karolyi.hu>,Atom,Glavin001_atom-beautify,1402678579,+0200,1,LICENSE.md;CHANGELOG.md;package.json;README.md
# Glavin Wiechert <glavin.wiechert@gmail.com>,Atom,Glavin001_atom-beautify,1410750268,-0300,1,package.json;CHANGELOG.md;LICENSE.md;README.md

#  Be sure to concatenate these together first and sort by the time column

import pandas as pd
import numpy as np
import csv
import pdb

infile = "ACC.csv"


reader = csv.DictReader(open(infile,"r"))

# Commit matrix:  ecosystems across, authors down
cmx = pd.DataFrame(dtype=np.int32)

def influences_authorwise():
    """At the current time, for each ecosystem E, what mix of other
    ecosystems F* have its users used?  For each user in E, and each
    other ecosystem F, add 1 to F-influences-E if that user has ever
    once committed to a project in F."""
    f_e = pd.DataFrame(data={ e:{e2:0 for e2 in cmx.columns}}, dptype=np.int32)
    for e in cmx.columns:
        for u in cmx.index:
            for e2 in cmx.columns:
                if cmx.loc[u,e1] > 0 and cmx.loc[u,e2]:
                    f_e.loc[e,e2] += 1
    return f_e


def influences_commitwise():
    """For each user U in E, and each
    other ecosystem F, multiply U's total commits in E by
    U's total commits in F, and add that to F-influences-E."""
    f_e = pd.DataFrame(data={ e:{e2:0 for e2 in cmx.columns}}, dptype=np.int32)
    for e in cmx.columns:
        for u in cmx.index:
            for e2 in cmx.columns:
                f_e.loc[e,e2] += cmx.loc[u,e1] * cmx.loc[u,e2]
    return f_e

pdb.set_trace()
for commit in reader:
    if commit["author"] not in cmx.index:
        cmx[commit["author"]] = 0
    cmx[commit["author"]][commit["eco"]] += 1

pdb.set_trace()
print influences_authorwise()

pdb.set_trace()
print influences_commitwise()

