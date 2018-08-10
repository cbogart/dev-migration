import csv
import glob

auths = dict()
for authact in glob.glob("/data/play/cbogart/authact.*.e.csv"):
    print "Reading ", authact
    for row in csv.DictReader(open(authact)):
        if row["author"] not in auths:
            auths[row["author"]] = set()
        auths[row["author"]].add(row["package"])

authproj = csv.writer(open("/data/play/cbogart/authprojs.csv","w"))
authproj.writerow(["author","project"])
for a in auths:
    for p in auths[a]:
        authproj.writerow([a,p])
        
