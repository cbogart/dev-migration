from oscar2 import *
import gzip
import csv
import pdb
import sys


ecos = sys.argv[1:] #"Atom Bioconductor Cargo CocoaPods CPAN CRAN Go Hackage Hex Lua Maven NPM NuGet Packagist Pypi Rubygems Stackage Eclipse".split(" ")
def ecop2c(eco): return  "data/fromOSCAR/prjlist.%s.p2c.b.gz" % (eco,)

def interesting(filename):
    end = filename.split("/")[-1]
    if len(end) < len(filename): return None
    if end[-2:]=="md" or end[-3:] == "txt" or end[-4:]=="json" or \
       end[-3:] == "xml" or "." not in end or end[-4:]=="toml" or \
       end[-2:] == "ac" or end[-3:] == "yml":
        return end
    else:
        return None

for eco in ecos:
    csvf = csv.writer(open("data/fromOSCAR/authact.%s.d.csv" % (eco,), "w"))
    csvf.writerow("author,eco,package,epoch,tz,core,files".split(","))
    #csvfe = csv.writer(open("data/fromOSCAR/authact.%s.err.csv" % (eco,), "w"))
    ##csvfe.writerow("sha,eco,package,error".split(","))
    print "\n", eco
    kount = 0
    pdb.set_trace()
    for p2c in gzip.open(ecop2c(eco)):
        kount += 1
        if kount % 1 == 0: print "...",kount
        parts = p2c.split(";")
        project = parts[0]
        shas = [s.strip() for s in parts[2:]]
        for sha in shas:
            try:
                commit = Commit(sha)
                author = commit.author
                when = commit.authored_at.split(" ")[0]
                tz = commit.authored_at.split(" ")[-1]
                files = "" # ";".join([i for i in [interesting(fn) for fn in commit.tree.files.keys()] if i is not None])
                csvf.writerow([author,eco,project,when,tz,1,files])
                #csvfe.writerow([sha,eco,project,"good"])
            except Exception, e:
                #csvfe.writerow([sha,eco,project,str(e)])
                pass
