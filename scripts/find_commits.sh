
for eco in Atom Bioconductor Cargo CocoaPods CPAN CRAN Go Hackage Hex Lua Maven NPM NuGet Packagist Pypi Rubygems Stackage
do
    cat data/fromLibrariesIo/${eco}-repos.txt | /da3_data/lookup/Prj2CmtShow.perl /da4_data/basemaps/Prj2CmtG 1 8 | gzip > data/fromOSCAR/prjlist.${eco}.p2c.b.gz
done
