import re
import pdb
import gzip
import csv
import glob
from collections import defaultdict

ecosystem_list = ["NPM", "Cargo", "Hex","Hackage","Stackage","CocoaPods","Rubygems","Pypi","Maven","Atom","LuaRocks","Go","CPAN","NuGet","Packagist","CRAN"]


# I. prep eco influence file for jupyter notebook
def I():
  csvout = csv.writer(open("data/notebook/eco_influence.csv","w"))
  csvout.writerow("from_eco,to_eco,year,influence,scaled_influence,commit_count".split(","))
  for f in glob.glob("data/laptop/graph_*.csv.gz"):
    if "_pkgs_" not in f:
        print f
        to_eco = re.search("graph_(.*)?.csv",f ).group(1)
        if to_eco not in ecosystem_list: continue
        for row in csv.DictReader(gzip.open(f)):
            csvout.writerow([row["influence"], to_eco, row["year"], 
               row["raw_influence"], float(row["raw_influence"])/float(row["raw_scale"]), row["commit_count"]])
I()

# II. Package influence table
#  Prepare from graph_pkg_*.csv
#year,package,influence,proportion,raw_influence,raw_scale,commit_count_package,commit_count_eco
#2010,Leont_sysv-sharedmem,CPAN,0.05,1020,1020,20,48502
#year,package,influence,proportion,raw_influence,raw_scale,commit_count_package,commit_count_eco,current_ecosystem_use
#2013,timjansen_PinkySwear.js,Maven,0.07692307692307693,2717,2717,13,1989302,702,1
#   nb. current_ecosystem_use is # of devs who worked on that package that year


commit_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))  # eco -> yr -> package -> counts
package_devs = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))  # eco -> yr -> package -> counts
def II():
  csvout = csv.writer(gzip.open("data/notebook/package_influence.csv.gz","w"))
  csvout.writerow("from_eco,year,in_eco,package,repo,influence,scaled_influence,influence_high,commit_count_package,commit_count_eco".split(","))
  for f in glob.glob("data/fromOSCAR/graph_aud_pkgs_*+p.csv.gz"):
    print f
    in_eco = re.search("graph_aud_pkgs_(.*)?\+p.csv.gz",f ).group(1)
    if in_eco not in ecosystem_list: continue
    for row in csv.DictReader(gzip.open(f)):
        csvout.writerow([row["influence"], row["year"], in_eco, row["package"], "UNKNOWN***",
           row["raw_influence"], float(row["raw_influence"])/float(row["raw_scale"]), row["raw_influence"] > 0,
           row["commit_count_package"], row["commit_count_eco"]])
        commit_counts[row["package"]][in_eco][row["year"]] += int(row["commit_count_package"])
        package_devs[row["package"]][in_eco][row["year"]] += int(row["current_ecosystem_use"])
II()

# IIIp. Package and Ecosystem Practices: pkg_releases.csv
#   Libraries.io:
#      ...find version and dependency constraint templatization code
#      ...change to be in terms of packages, not repos
#      ...incorporate in 10a_lib_project-rpractices-db (make releases.csv more awesome)
#      ...add release frequency, dep update freq, dep count at end of year, differential dep count
#      ...   mean_deps-updated, mean-proportion_deps-updated
#   Here: 
#      ...add commit counts per package from commit_counts variable above
#      ...SAVE age, reverse dependencies
#   OSCAR:
#      ...add estimated commit sizes 
#
# pkg_release.csv format:
#   year,eco,kind,package,count
#   1994,Packagist,release,maiden/maiden,2
#
def IIIp():
    csvout = csv.writer(gzip.open("data/notebook/package_practices.csv.gz","w"))
    package_prax = defaultdict(dict)   # eco/pkg/yr -> dict of practices
    all_practices = set()   # keep adding to this
    print "IIIp (pkg_releases.csv -> package_practices.csv.gz)"
    for row in csv.DictReader(gzip.open("data/libraries/pkg_releases.csv.gz")):
        if row["eco"] not in ecosystem_list: continue
        key = ",".join([row["eco"],row["package"],row["year"]])
        package_prax[key][row["kind"]] = int(row["count"])
        all_practices.add(row["kind"])
    for pkg in commit_counts:
        for eco in commit_counts[pkg]:
            if eco not in ecosystem_list: continue
            for yr in commit_counts[pkg][eco]:
                key = ",".join([eco,pkg,yr])
                #if key not in package_prax: 
                    #print "Surprise commit info: ", key
                    #pdb.set_trace()
                package_prax[key]["commits"] = commit_counts[pkg][eco][yr]
    all_practices = list(all_practices) + ["commits"]
    csvout.writerow("eco,package,year".split(",") + all_practices)
    for key in package_prax:
        csvout.writerow(key.split(",") + [package_prax[key].get(p,0) for p in all_practices])

def IIIe():
    print "IIIe (releases.csv -> ecosystem_practices.csv.gz)"
    csvout = csv.writer(gzip.open("data/notebook/ecosystem_practices.csv.gz","w"))
    ecosystem_prax = defaultdict(dict)   # eco/pkg/yr -> dict of practices
    all_practices = set()   # keep adding to this
    for row in csv.DictReader(gzip.open("data/libraries/releases.csv.gz")):
        if row["eco"] not in ecosystem_list: continue
        key = ",".join([row["eco"],row["year"]])
        ecosystem_prax[key][row["kind"]+"_count"] = int(float(row["count"]))
        ecosystem_prax[key][row["kind"]+"_proportion"] = float(row["proportion"])
        ecosystem_prax[key]["outof"] = int(float(row["outof"]))
        all_practices.add(row["kind"] + "_count")
        all_practices.add(row["kind"] + "_proportion")
        all_practices.add("outof")
    for pkg in commit_counts:
        for eco in commit_counts[pkg]:
            if eco not in ecosystem_list: continue
            for yr in commit_counts[pkg][eco]:
                key = ",".join([eco,yr])
                if "total_commits" not in ecosystem_prax[key]: ecosystem_prax[key]["total_commits"] = 0
                if "package_count" not in ecosystem_prax[key]: ecosystem_prax[key]["package_count"] = 0
                ecosystem_prax[key]["total_commits"] += commit_counts[pkg][eco][yr]
                ecosystem_prax[key]["package_count"] += 1
    for k in ecosystem_prax:
        try:
            ecosystem_prax[key]["average_commits"] = ecosystem_prax[key]["total_commits"]/ecosystem_prax[key]["package_count"]
        except Exception, e:
            print "ERROR calculating average commits for ", k, e, type(e)
            print "      total_commits=", ecosystem[key].get("total_commits","?")
            print "      package_count=", ecosystem[key].get("package_count","?")
    all_practices.update(["total_commits","package_count","average_commits"])
    all_practices = list(all_practices) + ["commits"]
    csvout.writerow("eco,year".split(",") + all_practices)
    for key in ecosystem_prax:
        csvout.writerow(key.split(",") + [ecosystem_prax[key].get(p,0) for p in all_practices])
IIIe()
IIIp()
    


# eco, package, year, vstyle1..N, dstyle1..N, ver_update_major, ver_update_minor, ver_update_patch, ver_update_supermajor,
#        ver_update_backport, release_frequency, dep_update_frequency, dep_count, new_dep_count, mean_deps_updated,
#        mean_proportion_deps_updated
#     +_by_commit_size suffix for versions&dependencies,
def IV():
    pass
IV()


# Package covariates
#   Here:
#     ... add commit counts per package, devs per package
#   Libraries.io
#     ... add reverse dependencies
#     ... add age
def IVa():
    pass
IVa()
