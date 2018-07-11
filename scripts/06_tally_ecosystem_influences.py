
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
import time
from collections import defaultdict

localfiles = "/data/play/cbogart/"
def epoch2yr(ep):
   return time.gmtime(int(ep)).tm_year 

cmts = csv.DictReader(gzip.open(localfiles + "unified.aud.csv.gz"))
logg = defaultdict(lambda: defaultdict( lambda:defaultdict(int)))
ecos = set()
cmtcount = defaultdict(lambda: defaultdict(int))
progress = 0
for row in cmts:
    progress += 1
    if progress%10000 == 0:
        print progress
    try:
        yr = epoch2yr(row["epoch"])
        logg[row["author"]][row["eco"]][yr] += 1
        cmtcount[row["eco"]][yr] += 1
    except:
        print "Can't read", row

ecos = cmtcount.keys()

cmts = csv.DictReader(gzip.open(localfiles + "unified.aud.csv.gz"))
infl = defaultdict(lambda: defaultdict( lambda:defaultdict(int)))
scale = defaultdict( lambda:defaultdict(int))
progress = 0
for row in cmts:
    progress += 1
    if progress%10000 == 0:
        print progress
    p = row["author"]
    eco = row["eco"]
    try:
        y = epoch2yr(row["epoch"])
        for f in ecos:
            for z in range(y-3,y):
                infl[f][eco][y] += logg[p][f][z]
                scale[eco][y] += logg[p][f][z]
    except Exception, e:
        print "can't use row", row

for eco in ecos:
    grph = csv.writer(open(localfiles + "graph_aud_" + eco + ".csv","w"))
    grph.writerow(["year","influence","proportion","raw_influence","raw_scale","commit_count"])
    for y in scale[eco].keys():
        for f in ecos:
            try:
                grph.writerow([y,f,1.0*infl[f][eco][y]/scale[eco][y]/cmtcount[eco][y],infl[f][eco][y],scale[eco][y],cmtcount[eco][y]])
            except Exception, e:
                print y,f,e

