import csv
import sys

emails = set()
for fname in sys.argv[1:]:
    print fname
    for row in csv.DictReader(open(fname,"r")):
        emails.add(row["author"])
    print len(emails), "emails detected so far"

with open("/data/play/cbogart/authors.csv","w") as f:
    for e in emails:
        f.write(e + "\n")
