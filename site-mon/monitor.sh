#!/bin/sh

TIMEOUT="240" 
#HOST="lcg-lrz-ce3.grid.lrz.de"
HOST="lcg-lrz-ce0.grid.lrz.de"
## HOST="lcg-lrz-ce1.grid.lrz.de"
#SCRIPT="/var/lib/qstat-mon/bin/parser-qstat.py"
SCRIPT="/var/lib/qstat-mon/bin/parser-squeue.py"

#FILTER="/var/lib/qstat-mon/bin/isascii-filter"
FILTER="/var/lib/qstat-mon/bin/isprint-filter"

# timeout $TIMEOUT ssh $HOST '. /etc/profile.d/sge.sh; qstat -t -ext -u \* -xml' | $FILTER | $SCRIPT
#sleep 2
#timeout $TIMEOUT ssh $HOST cat /tmp/squeue.log | $SCRIPT
sleep 1
timeout $TIMEOUT cat /lcg-lrz-ce3/qstat-mon/squeue.log | $SCRIPT
