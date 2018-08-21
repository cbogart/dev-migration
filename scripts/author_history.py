from oscar import *
import pickle
import re
import gzip
import csv
import pdb
import sys
import argparse

#
#  This script collects a person's entire history of contributions,
#   as well as contributions others have made on the same projects.
#   It takes into account best available information about the person's
#   set of alias emails
#  The "author" field is canonicalized to one of their aliases,
#   but if it's a different author, those are NOT canonicalized,
#   so don't take them literally except to mean "not this focal author"
#

# Algorithm:
# look up an author's aliases
# for each alias, get history of contributions:  project, date
#    for each contribution, if packagefile included, check if it changed
#    log each unique project
# for each project touched, get history of contributions: project, date
#    for each contribution, if packagefile included, check if it changed

ecosystems = "Atom Bioconductor Cargo CocoaPods CPAN CRAN Go Hackage Hex Lua Maven NPM NuGet Packagist Pypi Rubygems Stackage Eclipse".split(" ")
parser = argparse.ArgumentParser("Get a user's history to make a nice visualization")
parser.add_argument("--email", help="Email of the user", default="Jack Moffitt <jack@metajack.im>")
parser.add_argument("--aliases", help="dictionary of aliases", default="/data/play/cbogart/dev-migration/data/audrisAuthMap.dict")
parser.add_argument("--outfile", help="csv file to output commit list to", default="author_history.csv")
args, unknown = parser.parse_known_args()

print "Checking aliases..."
aliases = pickle.load(open(args.aliases, "rb"))
canon = aliases.get(args.email, "")
if canon == "":
    print args.email, ": user not found"
    canon = args.email
    aliases = [args.email]
else:
    aliases = [k for k in aliases if aliases[k] == canon]
assert canon in aliases, "Canonical email " + canon + " not in list"
assert args.email in aliases, "Provided email " + args.email + " not in list"
print "Aliases are: ", aliases

localfiles = "/data/play/cbogart/"
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

study_packages = dict()
nonstudy_packages = dict()
for eco in ecosystems:
    for name in open(projects(eco)).readlines():
        study_packages[name.strip()] = eco

def filelist2eco(files):
    if "package.json" in files: return "NPM"
    if "pom.xml" in files: return "Maven"
    if "Gemfile" in files: return "Rubygems"
    if "DESCRIPTION" in files: return "CRAN"
    if "Cargo.toml" in files: return "Cargo"
    return ""
    
def packages2eco(pkgs):    # returns (ecosystem, ourset)
    print "Extracting eco of ", pkgs
    found = set(pkgs).intersection(study_packages.keys())
    if len(found) > 0: return packages2eco(next(iter(found)))
    found = set(pkgs).intersection(nonstudy_packages.keys())
    if len(found) > 0: return packages2eco(next(iter(found)))
    return package2eco(pkgs[0])

def package2eco(pkg):    # returns (ecosystem, ourset)
    if pkg in study_packages: return (study_packages[pkg], 1)
    if pkg in nonstudy_packages: return (nonstudy_packages[pkg], 0)
    files = Project(pkg).head.tree.files.keys()
    eco = filelist2eco(files)
    nonstudy_packages[pkg] = eco
    return (eco, 0)

outf = csv.writer(open(args.outfile,"w"))
fields = ["author","sha","eco","study","project","when","ac_flag","pkg_change","differences"]
outf.writerow(fields)

all_projects = set()
commits = []
for alias in aliases:
    print "Checking commits by",alias
    auth = Author(alias)
    for commit in auth.commits:
        if len(commit.project_names) > 0:
            project_name = commit.project_names[0] 
            all_projects.add(project_name) 
            eco, study = package2eco(project_name)
        else:
            project_name = "(unknown project)"
            eco = filelist2eco(commit.tree.files.keys())
            study = 0
        acflag = commit.authored_at != commit.committed_at

        if packagefile(eco) in commit.tree.files.keys():
            newfilesha = commit.tree.files[packagefile(eco)] 
            pkg_change=True   # If the sha comparison fails, there's no parent, so we want ch=true
            try:
                oldfilesha = list(commit.parents)[0].tree.files.get(packagefile(eco),"no parent")
                pkg_change = newfilesha != oldfilesha
                newtext = Blob(newfilesha).data
                oldtext = Blob(oldfilesha).data
                difference = set(newtext.split("\n")).difference(set(oldtext.split("\n")))
            except:
                difference = "?"
        else:
            pkg_change = False
            difference = ""

        commits.append({
            "author": canon,
            "focal_author": True,
            "sha": commit.sha,
            "eco": eco,
            "project": project_name,
            "study": study,
            "when": commit.authored_at,
            "ac_flag": acflag,
            "differences": difference,
            "pkg_change": pkg_change})
        outf.writerow([commits[-1][fld] for fld in fields])
    print len(commits), "commits found"

if False:
  for i, prj in enumerate(all_projects):
    print "Checking commits in project ", i," of ", len(all_projects), "(",prj,")"
    p = Project(prj)
    eco, study = package2eco(prj)
    for commit in p.commits:
        acflag = commit.authored_at != commit.committed_at
        if packagefile(eco) in commit.tree.files.keys():
            newfilesha = commit.tree.files[packagefile(eco)] 
            oldfilesha = list(commit.parents)[0].tree.files.get(packagefile(eco),"no parent")
            pkg_change = newfilesha != oldfilesha
            try:
                newtext = Blob(newfilesha).data
                oldtext = Blob(oldfilesha).data
                difference = set(newtext.split("\n")).difference(set(oldtext.split("\n")))
            except:
                difference = "?"
        else:
            pkg_change = False
            difference = ""

        commits.append({
            "author": commit.author,
            "focal_author": commit.author in aliases,
            "sha": commit.sha,
            "eco": eco,
            "project": prj,
            "study": study,
            "when": commit.authored_at,
            "ac_flag": acflag,
            "differences": difference,
            "pkg_change": pkg_change})
        outf.writerow([commits[-1][fld] for fld in fields])
    print len(commits), "commits found"

#print "Rewriting", args.outfile
#for c in sorted(commits, key=lambda r: r["when"]):
    #f.writerow([c[fld] for fld in fields])


