import csv
import gzip
from collections import defaultdict

ecos = "Atom Bioconductor Cargo CocoaPods CPAN CRAN Go Hackage Hex Lua Maven NPM NuGet Packagist Pypi Rubygems Stackage Eclipse".split(" ") 

# year, package, influence
for dest in ecos:
    print "Doing",dest
    pkgs = defaultdict(lambda: defaultdict(int))   # pkg -> year -> infl
    for src in ecos:
        print "   Scanning",src
        inflf = csv.DictReader(gzip.open("data/laptop/infl/infl_pkg_" + src + "_to_" + dest + "_0.csv.gz"))
        for row in inflf:
            pkgs[row["package"]][row["year"]] += int(row["influence"])
    totalsf = csv.writer(gzip.open("data/laptop/infl/infl_total_pkg_" + dest + ".csv.gz","wb"))
    totalsf.writerow(["year","package","influence"])
    for p in pkgs:
        for y in pkgs[p]:
            totalsf.writerow([y,p,pkgs[p][y]])
    for src in ecos:
        print "   Rewriting",src
        inflf = csv.DictReader(gzip.open("data/laptop/infl/infl_pkg_" + src + "_to_" + dest + "_0.csv.gz"))
        outflf = csv.writer(gzip.open("data/laptop/infl/infl_pkg_normalized_" + src + "_to_" + dest + ".csv.gz", "wb"))
        outflf.writerow(["year","package","influence","infl_normalized"])
        for row in inflf:
            if pkgs[row["package"]][row["year"]] == 0:
                assert row["influence"] == "0", "Can't be"
                outflf.writerow([row["year"],row["package"],row["influence"], 0])
            else:
                outflf.writerow([row["year"],row["package"],row["influence"],
                     int(row["influence"])*1.0/pkgs[row["package"]][row["year"]]])
