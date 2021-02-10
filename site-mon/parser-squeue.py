#!/usr/bin/python

import sys, time
from subprocess import Popen, PIPE



# Folder for graphs and databases
eff_db = "/var/lib/qstat-mon/bin/eff.rrd"
noj_db = "/var/lib/qstat-mon/bin/noj.rrd"
graph_dir = "/var/www/qstat-mon/graph/" # accessible by php webinterface
graph_hist = "/var/www/qstat-mon/graph/history/"
user_graph_dir = "/var/www/qstat-mon/user/" # accessible by php webinterface
user_db = "/var/lib/qstat-mon/bin/users.db"
userlist_file = "/var/www/qstat-mon/userlist.dat" # accessible by php webinterface


jobs = []


running_atlasprd = 0
running_atlas_other = 0
running_other = 0
running_uh351bz = 0
waiting_atlasprd = 0
waiting_atlas_other = 0
waiting_other = 0
waiting_uh351bz = 0

debug = False

if "-D" in sys.argv:
	debug = True
	print "Switch on debug mode"


lines=sys.stdin.readlines()

for line in lines:
        wds = line.split()
        try:
                if wds[1].find('lcg') >= 0 :
                        user = wds[3]
                        state = wds[4]
                        ncore =  1
                        try:
                                ncore = int(wds[8])
			except:
				pass

                        if user == "atlasprd":
                                if ncore == 1:
	                                if state == "R":
	                                       	running_atlasprd += 1
                                	elif state == "PD":
                                        	waiting_atlasprd += 1
                        	else: # abuse muon calib id for mcore
                                	if state == "R":
                                        	running_uh351bz += ncore
                                	elif state == "PD":
                                        	waiting_uh351bz += 1
                        elif user.startswith("atlas"):
                                if state == "R":
                                        running_atlas_other += 1
                                elif state == "PD":
                                        waiting_atlas_other += 1
                        else:
                                if state == "R":
                                        running_other += 1
                                elif state == "PD":
                                        waiting_other += 1

        except:
                pass


running = running_atlasprd + running_atlas_other + running_other + running_uh351bz
waiting = waiting_atlasprd + waiting_atlas_other + waiting_other + waiting_uh351bz

if debug :
	print "running:, d, %d, %d, %d, %d " % ( running, running_atlasprd, running_atlas_other, running_other + running_uh351bz)
	print "waiting:, d, %d, %d, %d, %d " % ( waiting, waiting_atlasprd, waiting_atlas_other, waiting_other + waiting_uh351bz)


	
# update rrd databases
Popen("rrdtool update " + noj_db + " N:" + str(running_other) + ":" + str(running_atlas_other) + ":" + str(running_atlasprd) + ":" + str(running_uh351bz) + ":" + str(waiting_other+running_other) + ":" + str(waiting_atlas_other+running_atlas_other) + ":" + str(waiting_atlasprd+running_atlasprd) + ":" + str(waiting_uh351bz+running_uh351bz), shell=True).wait()


graph_name_noj = ["noj1h.png", "noj6h.png", "noj24h.png", "noj2d.png", "noj7d.png", "noj30d.png", "noj365d.png"]
start_time = ["-3600", "-21600", "-86400", "-172800", "-604800", "-2592000", "-31536000"]

for i in  range(7):

    arg4 = graph_dir + graph_name_noj[i] +  ' --start ' + start_time[i] + ' -a PNG -t "Number of running jobs" \
            --vertical-label "No. of jobs" -w 500 -h 300 -l 0 \
           DEF:graphe=' + noj_db + ':e:AVERAGE LINE1:graphe#f1a004:"waiting_other:dashes" \
           DEF:graphf=' + noj_db + ':f:AVERAGE LINE1:graphf#00FF00:"waiting_atlas_other:dashes" \
           DEF:graphg=' + noj_db + ':g:AVERAGE LINE1:graphg#0000FF:"waiting_atlasprd:dashes" \
           DEF:graphh=' + noj_db + ':h:AVERAGE LINE1:graphh#cb25ef:"waiting_mcore:dashes" \
           DEF:grapha=' + noj_db + ':a:AVERAGE LINE1:grapha#f1a004:"running_other" \
           DEF:graphb=' + noj_db + ':b:AVERAGE LINE1:graphb#00FF00:"running_atlas_other" \
           DEF:graphc=' + noj_db + ':c:AVERAGE LINE1:graphc#0000FF:"running_atlasprd" \
           DEF:graphd=' + noj_db + ':d:AVERAGE LINE1:graphd#cb25ef:"running_mcore" \
           COMMENT:"Total Jobs r/q  "' + str(running)  +'/' + str(waiting) + ' > /dev/null'
 		
#           COMMENT:"Total Jobs r/q: "' + str(running) + '"/"'  + str(waiting) + ' > /dev/null'

#	   COMMENT:"Total Jobs "' + str(running + waiting) + ' > /dev/null'


    Popen("rrdtool graph " + arg4, shell=True).wait()

    if debug:
	    print arg4


