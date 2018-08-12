from oscar import *
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


for eco in ecos:
    seen = set()
    projects_seen = set()
    errf = csv.writer(open(localfiles + "authactErrors.%s.csv" % (eco,), "w"))
    errf.writerow("package,sha,error".split(","))
    csvf = csv.writer(gzip.open(localfiles + "authactBehaviors.%s.csv.gz" % (eco,), "w"))
    csvf.writerow("author,eco,package,when,core,packagefile_update,msglen,msglines,poundref,numfiles,numparents,files".split(","))
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
                    packagefile_update = packagefile(eco) in commit.tree.files.keys()
                    numfiles = len(list(commit.tree.files))
                    poundref = re.search(r'#\d', commit.message) is not None
                    numparents = len(list(commit.parents))
                    csvf.writerow([author,eco,prj,when,1,packagefile_update,len(commit.message),len(commit.message.split("\n")),poundref,numfiles,numparents,";".join(list(commit.tree.files))])
                    seen.add(sha)
                    #csvfe.writerow([sha,eco,project,"good"])
                except Exception, e:
                    errf.writerow([project,sha,str(type(e)) + ":" + str(e)])
    pckf = csv.writer(open(localfiles + "foundpackages.%s.csv" % (eco,), "w"))
    pckf.writerow(["package"])
    for p in projects_seen(): pckf.writerow([p])
