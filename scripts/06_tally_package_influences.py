
#Input
#author,package,epoch,eco
#sambadevi <t.otlik93@gmail.com>,sambadevi_atom-devrant,1496862886,Atom
#sambadevi <t.otlik93@gmail.com>,sambadevi_atom-devrant,1496862982,Atom

#Output
#period,fromeco,toeco,fromcommits,tocommits,tototal,authcount,avg_fromcommits,avg_tocommits
#   fromcommits = # of commits by authors in toeco, made in fromeco in the previous 3 years
#   tocommits = # of commits by those same authors, in toeco, during period
#   authcount = number of people who committed both before and after
#   avg_fromcommits = average number of commits to from ecosystem in last 3 years by all the crossover people
#   avg_tocommits = average number of commits to to ecosystem in period by all the crossover people

import pdb
import csv
import gzip
import dill
import time
import sys
from collections import defaultdict

def epoch2yr(ep):
   return time.gmtime(int(ep)).tm_year 

localfiles = "/data/play/cbogart/"
unified = sys.argv[1]

cmts = csv.DictReader(gzip.open(unified))
logg = defaultdict(lambda: defaultdict( lambda:defaultdict(int)))
ecos = set()
cmtcount = defaultdict(lambda: defaultdict(int))
cmtcountp = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
progress = 0
for row in cmts:
    progress += 1
    if progress%100000 == 0:
        print progress
    try:
        yr = epoch2yr(row["epoch"])
        logg[row["author"]][row["eco"]][yr] += 1
        cmtcount[row["eco"]][yr] += 1
        cmtcountp[row["eco"]][row["package"]][yr] += 1
    except Exception, e:
        print "Can't read", row, e

ecos = cmtcount.keys()

cmts = csv.DictReader(gzip.open(unified))
infl = defaultdict(lambda: defaultdict(lambda: defaultdict( lambda:defaultdict(int))))
curr = defaultdict(lambda: defaultdict( lambda:defaultdict(int)))
scale = defaultdict(lambda: defaultdict( lambda:defaultdict(int)))
devs = defaultdict(lambda: defaultdict( lambda:defaultdict(set)))
progress = 0
for row in cmts:
    progress += 1
    if progress%100000 == 0:
        print progress
    p = row["author"]
    pkg = row["package"]
    eco = row["eco"]
    try:
        y = epoch2yr(row["epoch"])
        for f in ecos:
            for z in range(y-3,y):
                infl[f][eco][pkg][y] += logg[p][f][z]
                scale[eco][pkg][y] += logg[p][f][z]
        curr[eco][pkg][y] += logg[p][eco][y]
        devs[eco][pkg][y].add(p)
    except Exception, e:
        print "can't use row", row

print "Writing infl.dill"
dill.dump(infl,open(localfiles + "infl.dill","w"))
print "Writing cmtcountp.dill"
dill.dump(cmtcountp,open(localfiles + "cmtcount_pkgs.dill","w"))
print "Writing cmtcount.dill"
dill.dump(cmtcount,open(localfiles + "cmtcount.dill","w"))
print "done Writing cmtcount.dill"

for eco in ecos:
    grph = csv.writer(gzip.open(localfiles + "graph_aud_pkgs_" + eco + ".csv.gz","w"))
    grph.writerow(["year","repo","influence","proportion","raw_influence","raw_scale","commit_count_repo","commit_count_eco","current_ecosystem_use"])
    for pkg in scale[eco].keys():
      for y in scale[eco][pkg].keys():
        for f in ecos:
            try:
                grph.writerow([y,pkg,f,1.0*infl[f][eco][pkg][y]/scale[eco][pkg][y]/cmtcountp[eco][pkg][y],infl[f][eco][pkg][y],scale[eco][pkg][y],cmtcountp[eco][pkg][y],cmtcount[eco][y],curr[eco][pkg][y],len(devs[eco][pkg][y])])
            except Exception, e:
                print y,f,e

authlevel = csv.writer(gzip.open(localfiles + "authtotals.csv.gz"))
authlevel.writerow(["author","year","ecosystem","commits"])
for author in logg:
    for ecosystem in logg[author]:
        for year in logg[author][ecosystem]:
            authlevel.writerow([author,year,ecosystem,logg[author][ecosystem][year]])
