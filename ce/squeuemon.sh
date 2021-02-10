#!/bin/sh
outf=/tmp/squeue.log
squeue  -p lcg_serial  -o "%.18i %.9P %.8j %.8u %.2t %.10M %.6D %R  %C" > $outf.new 2>&1
mv $outf $outf.old
mv $outf.new $outf
