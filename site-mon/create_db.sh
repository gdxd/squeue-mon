#!/bin/sh

# creates the rrd databases in current folder that are needed by parser-qstat.py

rrdtool create eff.rrd --step 300 DS:a:GAUGE:600:U:U DS:b:GAUGE:600:U:U \
RRA:AVERAGE:0.5:1:12 \
RRA:AVERAGE:0.5:1:72 \
RRA:AVERAGE:0.5:2:144 \
RRA:AVERAGE:0.5:4:144 \
RRA:AVERAGE:0.5:4:504 \
RRA:AVERAGE:0.5:8:1080 \
RRA:AVERAGE:0.5:80:1314

rrdtool create noj.rrd --step 300 DS:a:GAUGE:600:U:U DS:b:GAUGE:600:U:U DS:c:GAUGE:600:U:U DS:d:GAUGE:600:U:U DS:e:GAUGE:600:U:U DS:f:GAUGE:600:U:U DS:g:GAUGE:600:U:U DS:h:GAUGE:600:U:U \
RRA:AVERAGE:0.5:1:12 \
RRA:AVERAGE:0.5:1:72 \
RRA:AVERAGE:0.5:2:144 \
RRA:AVERAGE:0.5:4:144 \
RRA:AVERAGE:0.5:4:504 \
RRA:AVERAGE:0.5:8:1080 \
RRA:AVERAGE:0.5:80:1314

 