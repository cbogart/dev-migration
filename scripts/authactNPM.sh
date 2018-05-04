
for prinfo in `gunzip -c data/fromOSCAR/prjlist.NPM.p2c.gz`
do
   PROJECT=`echo $prinfo | awk -F\; '{print $1}'`
   COMMITS=`echo $prinfo | cut -d\; -f3- | perl -ane 's/\;/\n/g;print'`
   WHENFO=`echo "$COMMITS" | /da3_data/lookup/showCmt.perl 0`
   echo "$WHENFO" | awk -F\; -v proj=$PROJECT -v eco=NPM '{print proj "," eco "," $4 "," $6}'
done
