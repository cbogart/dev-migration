import re
import gzip
import csv
import glob

# I. prep eco influence file for jupyter notebook
csvout = csv.writer(open("data/notebook/eco_influence.csv","w"))
csvout.writerow("from_eco,to_eco,year,influence,scaled_influence,commit_count".split(","))
for f in glob.glob("data/laptop/graph_*.csv"):
    print f
    to_eco = re.search("graph_(.*)?.csv",f ).group(1)
    for row in csv.DictReader(open(f)):
        csvout.writerow([row["influence"], to_eco, row["year"], 
           row["raw_influence"], float(row["raw_influence"])/float(row["raw_scale"]), row["commit_count"]])

#year,package,influence,proportion,raw_influence,raw_scale,commit_count_package,commit_count_eco
#2010,Leont_sysv-sharedmem,CPAN,0.05,1020,1020,20,48502

csvout = csv.writer(gzip.open("data/notebook/package_influence.csv.gz","w"))
csvout.writerow("from_eco,year,in_eco,package,repo,influence,scaled_influence,influence_high,commit_count_package,commit_count_eco".split(","))
for f in glob.glob("data/laptop/graph_pkgs_*.csv.gz"):
    print f
    in_eco = re.search("graph_pkgs_(.*)?.csv.gz",f ).group(1)
    for row in csv.DictReader(gzip.open(f)):
        csvout.writerow([row["influence"], row["year"], in_eco, row["package"], "UNKNOWN***",
           row["raw_influence"], float(row["raw_influence"])/float(row["raw_scale"]), row["raw_influence"] > 0,
           row["commit_count_package"], row["commit_count_eco"]])
