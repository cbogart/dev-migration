import dill
import sys
from collections import defaultdict
import gzip

infl = dill.load(open("/data/play/cbogart/infl.dill"))
print "Loaded influence data"

ecosystems = infl.keys()

for fromeco in ecosystems:
    for toeco in ecosystems:
        pkgs = defaultdict(lambda: defaultdict(int))
        print "Scanning", fromeco, "to", toeco
        inf = infl[fromeco][toeco]
        years = set()
        for pkg in inf:
            for yr in inf[pkg]:
                pkgs[pkg][yr] += inf[pkg][yr]
                years.add(yr)
        
        print "Writing", fromeco, "to", toeco
        import csv
        ou = csv.writer(gzip.open("/data/play/cbogart/infl_pkg_%s_to_%s_0.csv.gz" % (fromeco,toeco) ,"w"))
        ou.writerow("year,package,influence".split(","))
        for y in years:
            for p in pkgs:
                if y in pkgs[p]:
                    ou.writerow([y,p,pkgs[p][y]])
        
