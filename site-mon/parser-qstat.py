#!/usr/bin/python

import sys, time, sqlite3
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
from subprocess import Popen, PIPE

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# Folder for graphs and databases
eff_db = "/var/lib/qstat-mon/bin/eff.rrd"
noj_db = "/var/lib/qstat-mon/bin/noj.rrd"
graph_dir = "/var/www/qstat-mon/graph/" # accessible by php webinterface
graph_hist = "/var/www/qstat-mon/graph/history/"
user_graph_dir = "/var/www/qstat-mon/user/" # accessible by php webinterface
user_db = "/var/lib/qstat-mon/bin/users.db"
userlist_file = "/var/www/qstat-mon/userlist.dat" # accessible by php webinterface



jobs = []

class SGEQueueHandler(ContentHandler):
	element = ""
	state = ""
	project = ""
	owner = ""
	cpu_usage = ""
	wall_time = 0
	 
	 
	def __init__(self):
		self.tstart = time.time()
	
	 
	def startElement(self, name, attrs):
		self.element = name
	
		if name == "job_list":
			self.state = attrs.get("state")
	
	
	def characters(self, content):
		#on parse elements, if part of a <job_list>-element, in which case a stat is set
		if content.strip() != "" and self.state != "":
			#jobs of all states have an owner and a project
			if self.element == "JB_owner":
				self.owner = content
			elif self.element == "JB_project":
				self.project = content
			
			#parse additional data for running jobs
			if self.state == "running":
				if self.element  == "JAT_start_time":
					try:
						self.wall_time = self.tstart - time.mktime( time.strptime(content, "%Y-%m-%dT%H:%M:%S") )
					except:
						self.wall_time = 0
				elif self.element == "cpu_usage":
					self.cpu_usage = content
	 
	 
	def endElement(self, name):
		if name == "job_list":
			job = {}
			
			#ignore non-lcg jobs
			if self.project == "lcg":
				job["state"] = self.state
				job["owner"] = self.owner
				
				if self.state == "running":
					job["wall_time"] = self.wall_time
					job["cpu_usage"] = self.cpu_usage
				
				#"export" the current job
				jobs.append(job)
			
			#clear processing variables, for the next <job_list>-element
			self.element = ""
			self.state = ""
			self.project = ""
			self.owner = ""
			self.cpu_usage = ""
			self.wall_time = 0
				
#	if name == "job_list" and self.state == 1:

# parse xml input
handler = SGEQueueHandler()
parser = make_parser()
parser.setContentHandler(handler)
try:
    parser.parse(sys.stdin)
except Exception, x:
    print "SGE parsing trouble", x.__class__.__name__ , ':', x
    sys.exit(1)


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

for job in jobs:
	if job["owner"] == "atlasprd":
		if job["state"] == "running":
			running_atlasprd += 1
		elif job["state"] == "pending":
			waiting_atlasprd += 1
	elif job["owner"] == "uh351bz":
		if job["state"] == "running":
			running_uh351bz += 1
		elif job["state"] == "pending":
			waiting_uh351bz += 1
	elif job["owner"].startswith("atlas"):
		if job["state"] == "running":
			running_atlas_other += 1
		elif job["state"] == "pending":
			waiting_atlas_other += 1
	else:
		if job["state"] == "running":
			running_other += 1
		elif job["state"] == "pending":
			waiting_other += 1

running = running_atlasprd + running_atlas_other + running_other + running_uh351bz
waiting = waiting_atlasprd + waiting_atlas_other + waiting_other + waiting_uh351bz

if debug :
	print "running:, d, %d, %d, %d, %d " % ( running, running_atlasprd, running_atlas_other, running_other + running_uh351bz)
	print "waiting:, d, %d, %d, %d, %d " % ( waiting, waiting_atlasprd, waiting_atlas_other, waiting_other + waiting_uh351bz)




i = 0
j = 0
a = 0
b = 0
x = []
y = []
usermap = {}
for job in jobs:
	if job["state"] == "running":
		owner = job["owner"]
		eff = 0
		if job["wall_time"] > 300:
			try:
				eff = float(job["cpu_usage"]) / float(job["wall_time"])
			except:
				pass
		else:
			continue
		
		if owner == "atlasprd":
			a += eff
			i += 1
			x.append(eff)
		else:
			b += eff
			j += 1
			y.append(eff)
			try:
				usermap[owner].append(eff)
			except:
				usermap[owner] = [eff]


try:
	a /= i
except:
	a = 0

try:
	b /= j
except:
	b = 0

str_n =  str(i + j)

	
# update rrd databases
arg1 = eff_db + " N:" + str(a) + ":" + str(b)
Popen("rrdtool update " + arg1, shell=True).wait()

Popen("rrdtool update " + noj_db + " N:" + str(running_other) + ":" + str(running_atlas_other) + ":" + str(running_atlasprd) + ":" + str(running_uh351bz) + ":" + str(waiting_other+running_other) + ":" + str(waiting_atlas_other+running_atlas_other) + ":" + str(waiting_atlasprd+running_atlasprd) + ":" + str(waiting_uh351bz+running_uh351bz), shell=True).wait()

graph_name_avgeff = ["avgeff1h.png", "avgeff6h.png", "avgeff24h.png", "avgeff2d.png", "avgeff7d.png", "avgeff30d.png", "avgeff365d.png"]
graph_name_noj = ["noj1h.png", "noj6h.png", "noj24h.png", "noj2d.png", "noj7d.png", "noj30d.png", "noj365d.png"]
start_time = ["-3600", "-21600", "-86400", "-172800", "-604800", "-2592000", "-31536000"]

for i in  range(7):
    arg2 = graph_dir + graph_name_avgeff[i] +  ' --start ' + start_time[i] + ' -a PNG -t "Average Efficiency" \
            --vertical-label "Efficiency" -w 500 -h 300 -l 0 \
           DEF:grapha=' + eff_db + ':a:AVERAGE LINE1:grapha#ff0000:"atlasprd" \
           DEF:graphb=' + eff_db + ':b:AVERAGE LINE2:graphb#0000FF:"others" > /dev/null'

    arg4 = graph_dir + graph_name_noj[i] +  ' --start ' + start_time[i] + ' -a PNG -t "Number of running jobs" \
            --vertical-label "No. of jobs" -w 500 -h 300 -l 0 \
           DEF:graphe=' + noj_db + ':e:AVERAGE LINE1:graphe#f1a004:"waiting_other:dashes" \
           DEF:graphf=' + noj_db + ':f:AVERAGE LINE1:graphf#00FF00:"waiting_atlas_other:dashes" \
           DEF:graphg=' + noj_db + ':g:AVERAGE LINE1:graphg#0000FF:"waiting_atlasprd:dashes" \
           DEF:graphh=' + noj_db + ':h:AVERAGE LINE1:graphh#cb25ef:"waiting_muon:dashes" \
           DEF:grapha=' + noj_db + ':a:AVERAGE LINE1:grapha#f1a004:"running_other" \
           DEF:graphb=' + noj_db + ':b:AVERAGE LINE1:graphb#00FF00:"running_atlas_other" \
           DEF:graphc=' + noj_db + ':c:AVERAGE LINE1:graphc#0000FF:"running_atlasprd" \
           DEF:graphd=' + noj_db + ':d:AVERAGE LINE1:graphd#cb25ef:"running_muon" \
           COMMENT:"Total Jobs "' + str(running + waiting) + ' > /dev/null'

    Popen("rrdtool graph " + arg2, shell=True).wait()
    Popen("rrdtool graph " + arg4, shell=True).wait()

    if debug:
	    print arg2
	    print arg4

# make histograms with matplotlib
hour = False
ti = time.localtime()
if ti.tm_min <= 2:
     hour = True
     num = ti.tm_hour
 
t = time.strftime("%a %H:%M", ti)
 
# atlasprod
fig1 = plt.figure(figsize=(5, 4), dpi=100)
p1 = fig1.add_subplot(111)
p1.hist(x, 75, range=(0,1), facecolor='#ff0000', alpha=0.8)
p1.set_xlabel("ratio cpu/elapsed time")
p1.set_ylabel("no. of jobs")
p1.set_title("atlasprd    " + t)
p1.set_xlim(0, 1)
p1.grid(True)
plt.savefig(graph_dir + "atlasprd.png", bbox_inches='tight', dpi=100)
if hour:
    plt.savefig(graph_hist + "atlasprd" + str(num) + ".png", bbox_inches='tight', dpi=100)

# others
fig2 = plt.figure(figsize=(5, 4), dpi=100)
p2 = fig2.add_subplot(111)
p2.hist(y, 75, range=(0,1), facecolor='#0000FF', alpha=0.8)
p2.set_xlabel("ratio cpu/elapsed time")
p2.set_ylabel("no. of jobs")
p2.set_title("others    " + t)
p2.set_xlim(0, 1)
p2.grid(True)
plt.savefig(graph_dir + "others.png", bbox_inches='tight', dpi=100)
if hour:
    plt.savefig(graph_hist + "others" + str(num) + ".png", bbox_inches='tight', dpi=100)

cmd = "ssh lcg-lrz-ce2.grid.lrz-muenchen.de ./poolacct2DN.sh " 
connection = sqlite3.connect(user_db)
cursor = connection.cursor()
#cursor.execute("CREATE TABLE users (userid TEXT PRIMARY KEY, user TEXT, timestamp REAL)")

f = open(userlist_file, "w")

# userplots
for user, jobs in usermap.iteritems():
    u = (user,)
    username =""

##    cursor.execute('SELECT userid, user, timestamp FROM users WHERE userid=?', u)
##    usertupple = cursor.fetchone()
##    # found userid in database so check if timestamp is older then one week
##    if usertupple:
##        if time.time() - usertupple[2] < 604800:
##            username = usertupple[1]
##    # timestamp is too old so delete entry and get new username
##        else:
##            cursor.execute('DELETE FROM users where userid=?', u)
##            connection.commit()
##            p = Popen(cmd + user, shell=True, stdout=PIPE)
##            n = p.stdout.readline()
##            i = n.rfind("=")
##            n1 =  n[i+1:]
##            i = n1.rfind(":")
##            ti = time.time()
##            t = (user, n1[:i], ti)
##            cursor.execute('INSERT INTO users VALUES(?, ?, ?)', t)
##            connection.commit()
##            username = n1[:i]
##   
##    # userid not found in database so we have to get name
##    else:
##         p = Popen(cmd + user, shell=True, stdout=PIPE)
##         n = p.stdout.readline()
##         i = n.rfind("=")
##         n1 =  n[i+1:]
##         i = n1.rfind(":")
##         ti = time.time()
##         t = (user, n1[:i], ti)
##         cursor.execute('INSERT INTO users VALUES(?, ?, ?)', t)
##         connection.commit()
##         username = n1[:i]
    #GD patch
    username = user +"_" + username   
    #
    f.write( username + "\n")
    fig = plt.figure(figsize=(5, 4), dpi=100)
    p = fig.add_subplot(111)
    p.hist(jobs, 75, range=(0, 1), facecolor='#0000FF', alpha=0.8)
    p.set_xlabel("ratio cpu/elapsed time")
    p.set_ylabel("no. of jobs")
    p.set_title(username)
    p.set_xlim(0, 1)
    p.grid(True)
    plt.savefig(user_graph_dir + username + ".png", bbox_inches='tight', dpi=100)\

cursor.close()
f.close()

