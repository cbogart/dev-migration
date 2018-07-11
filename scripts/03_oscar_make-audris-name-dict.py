import csv
import pickle
from StringIO import StringIO
import pdb
import tarfile
import sys
csv.field_size_limit(sys.maxsize)

tf = tarfile.open("/home/audris/4096_matches.tgz", "r:gz")
members = tf.getmembers()
mapping = dict()
print "Searching", len(members), "files for matches"
mcount = 0
mapcount = 0
superlong = set()
superf = open("superlong.csv","w")
for member in members:
    print "file",mcount,"of",len(members),"dict size now",len(mapping),"mapping to",mapcount,"unique emails. Superlong=", len(superlong)
    mcount += 1
    if member.name != "cprojects.as":
        print member.name
        csvf = csv.reader(tf.extractfile(member), delimiter=";", quoting=csv.QUOTE_NONE)
        try:
          for row in csvf:
            if max([len(k) for k in row]) > 1000:
                superlong.add(";".join(row))
                superf.write(";".join(row)+"\n")
            if len(row[4]) > 0 and len(row[5]) > 0:
                if (row[4] in mapping and row[5] in mapping):
                    pass
                if (row[4] in mapping and not row[5] in mapping):
                    mapping[row[5]] = mapping[row[4]]
                if (row[5] in mapping and not row[4] in mapping):
                    mapping[row[4]] = mapping[row[5]]
                if (not row[5] in mapping and not row[4] in mapping):
                    mapping[row[4]] = row[5]
                    mapping[row[5]] = row[5]
                    mapcount += 1
        except Exception, e:
            print row, e

#print "Josef Kriz <pepakriz@gmail.com> has ", len(mapping["Josef Kriz <pepakriz@gmail.com>"]), "aliases.  Lengths are", ",".join([len(k) for k in mapping["Josef Kriz <pepakriz@gmail.com>"]])
                
pickle.dump(mapping, open("audrisAuthMap.dict", "w"))
