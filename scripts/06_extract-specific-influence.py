import dill
import sys
from collections import defaultdict

infl = dill.load(open("/data/play/cbogart/infl.dill"))
fromeco = sys.argv[1]
toeco = sys.argv[2]
print "Loaded influence data"

pkgs = defaultdict(lambda: defaultdict(int))
inf = infl[fromeco][toeco]
years = set()
for pkg in inf:
    print pkg
    for yr in inf[pkg]:
        pkgs[pkg][yr] += inf[pkg][yr]
        years.add(yr)

print "Writing"
import csv
ou = csv.writer(open("/data/play/cbogart/infl_pkg.csv","w"))
ou.writerow("year,package,influence".split(","))
for y in years:
    for p in pkgs:
        if y in pkgs[p]:
            ou.writerow([y,p,pkgs[p][y]])

