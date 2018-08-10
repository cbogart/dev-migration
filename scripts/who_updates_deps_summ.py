from oscar import *
from collections import defaultdict
import re
import gzip
import csv
import pdb
import sys


localfiles = "/data/play/cbogart/"
ecos = sys.argv[1:] #"Atom Bioconductor Cargo CocoaPods CPAN CRAN Go Hackage Hex Lua Maven NPM NuGet Packagist Pypi Rubygems Stackage Eclipse".split(" ")
def projects(eco): return "data/common/%s-repos.txt" % (eco,)
def packagefile(eco):
    if eco == "NPM": return "package.json"
    elif eco == "Atom": return "package.json"
    elif eco == "tester": return "DESCRIPTION"
    elif eco == "Maven": return "pom.xml"
    elif eco == "Rubygems": return "Gemfile"
    elif eco == "CRAN": return "DESCRIPTION"
    elif eco == "Cargo": return "Cargo.toml"
    elif eco == "Bioconductor": return "DESCRIPTION"
    else: return "UNKNOWN_file"

def interesting(filename):
    end = filename.split("/")[-1]
    if len(end) < len(filename): return None
    if end[-2:]=="md" or end[-3:] == "txt" or end[-4:]=="json" or \
       end[-3:] == "xml" or "." not in end or end[-4:]=="toml" or \
       end[-2:] == "ac" or end[-3:] == "yml":
        return end
    else:
        return None

def period(t):
    return t.isoformat()[:7]

for eco in ecos:
    seen = set()
    projects_seen = set()
    errf = csv.writer(open(localfiles + "authactErrors.%s.csv" % (eco,), "w"))
    errf.writerow("package,sha,error".split(","))
    authinfo = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))   # author -> period -> measure -> count
    apinfo = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))   # author -> projdct-> period -> measure -> count
    prjinfo = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))   # author -> period -> measure -> count
    print "\n", eco
    for project in open(projects(eco)).readlines():
        prj = project.strip()
        print prj
        for sha in Project(prj).commit_shas:
            if sha not in seen:
                try:
                    projects_seen.add(prj)
                    commit = Commit(sha)
                    author = commit.author
                    when = commit.authored_at
                    #files = (list(commit.tree.files))
                    files = []
                    packagefile_update = packagefile(eco) in files
                    readme = 1 if len([f for f in files if (f.lower().startswith("readme") and "/" not in f)]) > 0 else 0
                    change = 1 if len([f for f in files if (f.lower().startswith("change") and "/" not in f)]) > 0 else 0
                    license = 1 if len([f for f in files if (f.lower().startswith("license") and "/" not in f)]) > 0 else 0
                    numfiles = len(files)
                    poundref = re.search(r'#\d', commit.message) is not None
                    numparents = len(list(commit.parents))
                    prjinfo[prj][period(when)]["packagefile_update"] += packagefile_update
                    prjinfo[prj][period(when)]["msglen"] += len(commit.message)
                    prjinfo[prj][period(when)]["msglines"] += len(commit.message.split("\n"))
                    prjinfo[prj][period(when)]["poundref"] += 1 if poundref else 0
                    prjinfo[prj][period(when)]["numfiles"] += numfiles
                    prjinfo[prj][period(when)]["numparents"] += numparents
                    prjinfo[prj][period(when)]["count"] += 1
                    prjinfo[prj][period(when)]["readme"] += readme
                    prjinfo[prj][period(when)]["change"] += change
                    prjinfo[prj][period(when)]["license"] += license
                    authinfo[author][period(when)]["packagefile_update"] += packagefile_update
                    authinfo[author][period(when)]["msglen"] += len(commit.message)
                    authinfo[author][period(when)]["msglines"] += len(commit.message.split("\n"))
                    authinfo[author][period(when)]["poundref"] += 1 if poundref else 0
                    authinfo[author][period(when)]["numfiles"] += numfiles
                    authinfo[author][period(when)]["numparents"] += numparents
                    authinfo[author][period(when)]["count"] += 1
                    authinfo[author][period(when)]["readme"] += readme
                    authinfo[author][period(when)]["change"] += change
                    authinfo[author][period(when)]["license"] += license
                    #csvf.writerow([author,eco,prj,when,1,packagefile_update,len(commit.message),len(commit.message.split("\n")),poundref,numfiles,numparents,";".join(list(commit.tree.files))])
                    apinfo[author][prj][period(when)]["packagefile_update"] += packagefile_update
                    apinfo[author][prj][period(when)]["msglen"] += len(commit.message)
                    apinfo[author][prj][period(when)]["msglines"] += len(commit.message.split("\n"))
                    apinfo[author][prj][period(when)]["poundref"] += 1 if poundref else 0
                    apinfo[author][prj][period(when)]["numfiles"] += numfiles
                    apinfo[author][prj][period(when)]["numparents"] += numparents
                    apinfo[author][prj][period(when)]["count"] += 1
                    apinfo[author][prj][period(when)]["readme"] += readme
                    apinfo[author][prj][period(when)]["change"] += change
                    apinfo[author][prj][period(when)]["license"] += license
                    #csvf.writerow([author,eco,prj,when,1,packagefile_update,len(commit.message),len(commit.message.split("\n")),poundref,numfiles,numparents,";".join(list(commit.tree.files))])
                    seen.add(sha)
                    #csvfe.writerow([sha,eco,project,"good"])
                except Exception, e:
                    errf.writerow([project,sha,str(type(e)) + ":" + str(e)])
    pckf = csv.writer(open(localfiles + "foundpackages.%s.csv" % (eco,), "w"))
    pckf.writerow(["package"])
    flds = "packagefile_update,msglen,msglines,poundref,numfiles,numparents,count,readme,license,change".split(",")
    authf = csv.writer(gzip.open(localfiles + "authactBehaviors.%s.csv.gz" % (eco,), "w"))
    authf.writerow("author,period,packagefile_update,msglen,msglines,poundref,numfiles,numparents,count,readme,change,license".split(","))
    apf = csv.writer(gzip.open(localfiles + "authPrjBehaviors.%s.csv.gz" % (eco,), "w"))
    apf.writerow("author,project,period,packagefile_update,msglen,msglines,poundref,numfiles,numparents,count,readme,change,license".split(","))
    pkgf = csv.writer(gzip.open(localfiles + "packageBehaviors.%s.csv.gz" % (eco,), "w"))
    pkgf.writerow("package,period,packagefile_update,msglen,msglines,poundref,numfiles,numparents,count,readme,change,license".split(","))
    for p in projects_seen: pckf.writerow([p])
    for p in prjinfo:
        for pd in prjinfo[p]:
            pkgf.writerow([p,pd] + [prjinfo[p][pd][k] for k in flds])
    for a in authinfo:
        for pd in authinfo[a]:
            authf.writerow([a,pd] + [authinfo[a][pd][k] for k in flds])
    for a in apinfo:
      for p in apinfo[a]:
        for pd in apinfo[a][p]:
            apf.writerow([a,p,pd] + [apinfo[a][p][pd][k] for k in flds])
