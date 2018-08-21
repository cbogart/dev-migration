import csv
import gzip
import argparse
from collections import defaultdict

parser = argparse.ArgumentParser(description="Find people in two ecosystems who edited their package.json or equivalent")
parser.add_argument("--eco1", help="First ecosystem", default="Cargo")
parser.add_argument("--eco2", help="Second ecosystem", default="NPM")
args, unknown = parser.parse_known_args()

'''author,period,packagefile_update,msglen,msglines,poundref,numfiles,numparents,count,readme,change,license
   Erick Romero <Zyst@users.noreply.github.com>,2017-03,0,18,1,1,0,1,1,0,0,0
'''

people = defaultdict(list)
both = defaultdict(list)
print "Reading ", args.eco1
for ppl in csv.DictReader(gzip.open("/data/play/cbogart/authactBehaviors." + args.eco1 + ".csv.gz")):
    if ppl["packagefile_update"] > 0:
        people[ppl["author"]].append([args.eco1, ppl["period"]])

print "Reading ", args.eco2
for ppl in csv.DictReader(gzip.open("/data/play/cbogart/authactBehaviors." + args.eco2 + ".csv.gz")):
    if ppl["packagefile_update"] > 0 and ppl["author"] in people:
        if ppl["author"] not in both:
            both[ppl["author"]] = people[ppl["author"]]
        both[ppl["author"]].append([args.eco2, ppl["period"]])

for who in both:
    print who
    print "\t" + "\n\t".join([str(k) for k in sorted(both[who], key=lambda (k): k[1])])
