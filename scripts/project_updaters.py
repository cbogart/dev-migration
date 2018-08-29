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

ecosystems = ["CRAN"] #"Atom Bioconductor Cargo CocoaPods CPAN CRAN Go Hackage Hex Lua Maven NPM NuGet Packagist Pypi Rubygems Stackage Eclipse".split(" ")
parser = argparse.ArgumentParser("Get a project's history to see who updated its version")
parser.add_argument("--project", help="github owner/name of the project", default="macroevolution/bammtools")
parser.add_argument("--aliases", help="dictionary of user aliases", default="/data/play/cbogart/dev-migration/data/audrisAuthMap.dict")
parser.add_argument("--outfile", help="csv file to output commit list to", default="project_updaters.csv")
args, unknown = parser.parse_known_args()

print "Checking aliases..."
aliases = pickle.load(open(args.aliases, "rb"))

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

def versionstring(eco):
    if eco == "CRAN": return r"""^Version:\s+(.*+)$"""
    else return "UNKNOWN"

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

p = Project(args.project)
eco, study = package2eco(args.project)
if eco not in ecosystems:
    print "This project is ", eco, ", not in ", ecosystems,"!"
   
for commit in p.commits:
        acflag = commit.authored_at != commit.committed_at
        if packagefile(eco) in commit.tree.files.keys():
            newfilesha = commit.tree.files[packagefile(eco)] 
            oldfilesha = list(commit.parents)[0].tree.files.get(packagefile(eco),"no parent")
            pkg_change = newfilesha != oldfilesha
            try:
                newtext = Blob(newfilesha).data.split("\n")
                oldtext = Blob(oldfilesha).data.split("\n")
                added = [line for line in set(newtext).difference(set(oldtext)) if 
To do: preload this regex, and check it here
                subtracted = set(oldtext).difference(set(newtext))
Also, cf added/subtracted to see if major/minor change.  OR decide to do this later?
            except:
                added = set()
                subtracted = set()
        else:
            pkg_change = False
            added = set()
            subtracted = set()

        commits.append({
            "author": commit.author,
            "focal_author": commit.author in aliases,
            "sha": commit.sha,
            "eco": eco,
            "project": prj,
            "study": study,
            "when": commit.authored_at,
            "ac_flag": acflag,
            "differences": ";".join(added) + "|" + ";".join(subtracted),
            "pkg_change": pkg_change})
        outf.writerow([commits[-1][fld] for fld in fields])
    print len(commits), "commits found"

#print "Rewriting", args.outfile
#for c in sorted(commits, key=lambda r: r["when"]):
    #f.writerow([c[fld] for fld in fields])


