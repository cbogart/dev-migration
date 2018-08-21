import re
import pdb
import gzip
import csv
import glob
import random
from collections import defaultdict
#"LuaRocks",
ecosystem_list = ["NPM", "Cargo", "Hex","Hackage","Stackage","CocoaPods","Rubygems","Pypi","Maven","Atom","Go","CPAN","NuGet","Packagist","CRAN"]
#ecosystem_list = ["Packagist","CPAN"]

# A. from_eco,year,in_eco,package,repo,influence,scaled_influence,influence_high,commit_count_package,commit_count_eco,
#         doesmajor1,doesmajor2,depnomajor,has000,majorsize,releasesize,majorrelsize,doesbackport,doesreleases,

#  Prepare from graph_pkg_*.csv
#year,package,influence,proportion,raw_influence,raw_scale,commit_count_package,commit_count_eco
#2010,Leont_sysv-sharedmem,CPAN,0.05,1020,1020,20,48502
#year,package,influence,proportion,raw_influence,raw_scale,commit_count_package,commit_count_eco,current_ecosystem_use
#2013,timjansen_PinkySwear.js,Maven,0.07692307692307693,2717,2717,13,1989302,702,1
#   nb. current_ecosystem_use is # of devs who worked on that package that year


commit_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))  # eco -> yr -> package -> counts
package_devs = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))  # eco -> yr -> package -> counts
def A():
  csvout = csv.writer(open("data/notebook/package_stats2.csv","w"))

  package_prax = defaultdict(dict)   # eco/pkg/yr -> dict of practices
  all_practices = set()   # keep adding to this
  influences = set()
  for in_eco in ecosystem_list:
      print in_eco
      for row in csv.DictReader(gzip.open("data/fromOSCAR/graph_aud_pkgs_" + in_eco + "+p.csv.gz")):
          key = ",".join([in_eco,row["package"],row["year"]])
          package_prax[key]["influence_" + row["influence"]] = row["raw_influence"]
          package_prax[key]["scaled_influence_" + row["influence"]] = float(row["raw_influence"])/float(row["raw_scale"])
          package_prax[key]["high_influence_" + row["influence"]] = row["raw_influence"] > 0
          package_prax[key]["commits"] = row["commit_count_package"]
          package_prax[key]["commit_count_eco"] = row["commit_count_eco"]
          package_prax[key]["distinct_devs"] = int(row["current_ecosystem_use"])
          influences.update(set(package_prax[key].keys()))
  prcount = 0
  for row in csv.DictReader(gzip.open("data/libraries/pkg_releases.csv.gz")):
      prcount += 1
      if prcount % 100000 == 0: print prcount, "of about 10,000,000, (", prcount*100/10000000,"%)"
      if row["eco"] not in ecosystem_list: continue
      key = ",".join([row["eco"],row["package"],row["year"]])
      package_prax[key][row["kind"]] = float(row["count"])
      #all_practices.add(row["kind"])
  print "Writing out output table"
  all_practices = list(all_practices) + ["commits"]
  some_practices = ["founded","total_deps","reverse_dependencies","change_dep","add_dep","deps_added_per_year","dep_situation_altered_per_year"]
  metrics = ["doesmajor1","doesmajor2","depnomajor","has000","major_ratio","backport_ratio","doesbackports","doesreleases"]

  lookups = list(influences) + some_practices + ["commits"]
  headers = lookups  + list(metrics)
  csvout.writerow("eco,package,year".split(",") + headers)
  for key in package_prax:
      # Calculate columns
      if package_prax[key].get("release",0) > 0:
          row = package_prax[key]
          doesmajor1 = int(row.get("major",0) > 0)
          doesmajor2 = int(row.get("major",0) > 1)
          depnomajor = int(row.get("dep_form_nonmajor",0) > 0)
          has000 = int(row.get("version_form_0.0.0",0) > 0)
          major_ratio = row.get("major",0)/row.get("release",1)
          backport_ratio = row.get("backport",0)/row.get("release",1)
          doesbackports = int(row.get("backport",0) > 0)
          doesreleases = int(row.get("release",0) > 0 )  # should always be 1
          csvout.writerow(key.split(",") + [package_prax[key].get(p,0) for p in lookups ] + [
            doesmajor1, doesmajor2,depnomajor,has000,major_ratio, backport_ratio,
            doesbackports,doesreleases])
A()
