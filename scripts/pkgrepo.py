import argparse
import pdb
import csv
import gzip

# host,repo,ecosystem,packageID,packageName
#Bitbucket,davidcsejtei_wp-tooler,Packagist,1478617,davidcsejtei/davidcsejtei-wp-lib

parser = argparse.ArgumentParser(description="Add a package or repo column (whichever is missing) to a csv file, looking up the mapping in another mapping file")
parser.add_argument('--pkg_repo_map', help='Mapping between packages and repositories',
    default='data/common/pkg-repo-map.csv')
parser.add_argument('incsv', help='File to map')
parser.add_argument('outcsv', help='New expanded version of file')
args, unknown = parser.parse_known_args()


print "Loading map..."
repo_lookup = dict()
pkg_lookup = dict()
for row in csv.DictReader(open(args.pkg_repo_map)):
    repo_lookup[row["packageName"]] = row["repo"]
    pkg_lookup[row["repo"]] = row["packageName"]
print "  ....Done"


if args.outcsv.endswith("gz"):
    outcsv = csv.writer(gzip.open(args.outcsv,"w"))
else:
    outcsv = csv.writer(open(args.outcsv,"w"))

if args.incsv.endswith("gz"):
    incsv = csv.DictReader(gzip.open(args.incsv))
else:
    incsv = csv.DictReader(open(args.incsv))

if "package" in incsv.fieldnames and "repo" not in incsv.fieldnames:
    mapping = {"repo": ("package", repo_lookup)}
if "project" in incsv.fieldnames and "package" not in incsv.fieldnames:
    mapping = {"package": ("project", pkg_lookup)}
if "repo" in incsv.fieldnames and "package" not in incsv.fieldnames:
    mapping = {"package": ("repo", pkg_lookup)}

newheaders = incsv.fieldnames + mapping.keys()
outcsv.writerow(newheaders)
for row in incsv:
  try:
    outcsv.writerow([
        mapping[h][1].get(row[mapping[h][0]],"UNKNOWN " + h + ":" + row[mapping[h][0]]) if h in mapping else row[h]
        for h in newheaders])
  except Exception, e:
    pdb.set_trace()
    print e


