#!/usr/bin/python

import sys, os, time, atexit
from signal import SIGTERM 
 
class Daemon:

    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit first parent
                sys.exit(0) 
        except OSError, e: 
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
            
        # decouple from parent environment
        os.chdir("/") 
        os.setsid() 
        os.umask(0) 
        
        # do second fork
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit from second parent
                sys.exit(0) 
        except OSError, e: 
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1) 
        
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        
        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)
        
    def delpid(self):
        os.remove(self.pidfile)
 
    def start(self):
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
            
            if pid:
                message = "pidfile %s already exist. Daemon already running?\n"
                sys.stderr.write(message % self.pidfile)
                sys.exit(1)
                
        # Start the daemon
        self.daemonize()
        self.run()
 
    def stop(self):

        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
            
        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart
 
        # Try killing the daemon process        
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
                else:
                    print str(err)
                    sys.exit(1)
 
    def restart(self):
        self.stop()
        self.start()
                
    def run(self):
        pass

import datetime
import imp
import settings
import django
from django.core.management import setup_environ

DIR=os.path.abspath(__file__)
sys.path.append(imp.find_module("django")[1])
sys.path.append(os.path.split(os.path.split(DIR)[0])[0])
setup_environ(settings)


class ComponentError(Exception):
    def __init__(self,component,components):
        self.components=components
        self.component=component
    def __str__(self):
        return "Invalid component:"+self.component+". Available components: "+",".join(self.components)
		

class BaseCron(Daemon):
    def __init__(self, pid):
        Daemon.__init__(self, pid)
        self.events={}
        self.components=["year","month","day","hour","minute","second"]

    def add_event(self,event,period,component,round=False):
        if not self.components.count(component):
            raise ComponentError(component,self.components)
        self.events[event]={"period":period,"component":component,"round":round}
        self.find_next(event)

    def find_next(self,event):
	now=datetime.datetime.now()
	comps={"year":now.year,
		"month":now.month,
		"day":now.day,
		"hour":now.hour,
		"minute":now.minute,
		"second":now.second}
	component=self.events[event]["component"]
	period=self.events[event]["period"]
	if component=="year":
		comps[component]+=period
	elif component=="month":
		comps[component]=range(1, 13)[(now.month+period-1)%12]
		if comps[component]==1:comps["year"]+=1
	else:
		karg={component+"s":period}	
		time_delta=datetime.timedelta(**karg)
		next=now+time_delta
		comps={"year":next.year,
				"month":next.month,
				"day":next.day,
				"hour":next.hour,
				"minute":next.minute,
				"second":next.second}
	round=self.events[event]["round"]
	if round:
            for comp in self.components[self.components.index(component)+1:]:
                    comps[comp]=1
	next_visit=datetime.datetime(**comps)
	self.events[event]["next_visit"]=next_visit

    def run(self):
        while 1:
            ###sorting job###
            list=[(self.events[x]["next_visit"],x) for x in self.events.keys()]
            list.sort()
            event_name=list[0][1]
            event_date=list[0][0]
            now=datetime.datetime.now()
            timedelta=event_date-now         
            seconds=(timedelta.days*24*60*60)+timedelta.seconds
            print "\nnext job: '"+event_name +"' after:", str(timedelta)
            if timedelta.days>=0:
                while seconds:
                        if seconds>1000:
                                time.sleep(1000)
                                seconds-=1000
                        else:
                                time.sleep(seconds)
                                seconds=0
                        
                time.sleep(seconds)
            print "processing job..."
            getattr(self,event_name)()
            print "finished succesfully."
            self.find_next(event_name)

from django.db.models.loading import get_apps
get_apps()

#########################################################
#########YOU DONT NEED TO CHANGE ANYTHING ABOVE##########
#########################################################

# application specific code starts here
import poplib
import email
from email.header import decode_header
import re
import StringIO
import Image

from django.conf import settings
from pullaclub.members.models import Comment
from django.contrib.auth.models import User

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def remove_extra_spaces(data):
    p = re.compile(r'\s+')
    return p.sub(' ', data)

def strip_mms_html(html):
    p = re.compile(r'<title>.*</title>')
    return remove_extra_spaces(remove_html_tags(p.sub('',html,re.I)))

def dump_mail(message, idx):
    f = open('/tmp/msg-'+idx+'.txt','wb') # should not write to tmp
    f.write('\n'.join(message))
    f.close()
    
class StringIOWrapper(StringIO.StringIO):

    def chunks(self, chunk_size=None):
        self.seek(0)
        yield self.read()

    def __len__(self):
        self.seek(0,2)
        return self.tell()

def process_mailbox():

    print '{0}@{1} - start- polling'.format(settings.POP_USERNAME,settings.POP_HOST)
    mailbox = poplib.POP3(settings.POP_HOST)
    mailbox.user(settings.POP_USERNAME)
    mailbox.pass_(settings.POP_PASSWORD)
    
    (message_count, mailbox_size) = mailbox.stat()

    if message_count == 0: # nothing to do
        print '{0}@{1} - end - no messages'.format(settings.POP_USERNAME,settings.POP_HOST)
        mailbox.quit()
        return

    print '{0}@{1} - process - {2} new messages'.format(settings.POP_USERNAME,settings.POP_HOST, message_count)

    user = User.objects.get(username=settings.MMS_USER)

    for message in mailbox.list()[1]:
        idx,_ = message.split()
        resp = mailbox.retr(idx)
        
        #dump_mail(resp[1],idx)  # debug
        newcomment = Comment()
        newcomment.user = user
    
        parsedmsg = email.message_from_string('\n'.join(resp[1]))
        (subject, enc) = decode_header(parsedmsg['Subject'])[0]
        sender = parsedmsg['From']
        description = ''
        has_image = False

        print '{0}@{1} - mail - {2} ({3}) - processing'.format(settings.POP_USERNAME,settings.POP_HOST, sender,subject)

        for msgpart in parsedmsg.walk():
            ctype = msgpart.get_content_type()

            if ctype == 'text/plain':
                description = msgpart.get_payload(decode=True)

            elif ctype == 'text/html' and description == '':
                # use html text only if plain text not available
                description = strip_mms_html(msgpart.get_payload(decode=True))
                
            elif ctype.startswith('image/') and not has_image:
                filename = msgpart.get_filename()
                filename = 'mms-'+filename.split('/')[-1]

                mfile = StringIOWrapper(msgpart.get_payload(decode=True))
                try:
                    Image.open(mfile)
                except IOError,e:
                    print '{0}@{1} - mail - {2} ({3}) - {4} failed {5}'.format(settings.POP_USERNAME,settings.POP_HOST, sender,subject,filename,str(e))
                else:
                    newcomment.image0.save(filename,mfile)
                    has_image = True
                
                print '{0}@{1} - mail - {2} ({3}) - {4} stored'.format(settings.POP_USERNAME,settings.POP_HOST, sender,subject,filename)
                
        #mailbox.dele(idx)
        description = sender +" "+subject + ": "+description
        newcomment.message = description
        #newcomment.save()

    print '{0}@{1} - end'.format(settings.POP_USERNAME,settings.POP_HOST)    
    mailbox.quit()


class MMSCron(BaseCron):
    def __init__(self,pid):
        BaseCron.__init__(self,pid)
        self.add_event("mms_email_poll_job",5,"minute",round=True)
		
    def mms_email_poll_job(self):
        process_mailbox()



"""
####DETAILS#####

add_event function adds  a new job to schedule.
-first argument is function name
-second is period length
-third is period component ("second","minute","hour","day","month" or "year"
-last one tells if time should be rounded to period component
otherwise function will be called without taking care of component
head.
	

name this script and put this script in your projects folder to the
same level with your settings.py. a pid file will be automatically
created into your project's folder

#####SHELL COMMANDS######

to start:
python deamon.py start

to restart:
python deamon.py restart

to stop:
python deamon.py stop

if you are running on a windows environment or just want to test how it works
use:
python deamon.py run

"""


if __name__ == "__main__":

    daemon = MMSCron(os.path.join(os.path.split(DIR)[0],'django-cron-daemon.pid'))
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'run'== sys.argv[1]:
            daemon.run()
        elif 'runonce'== sys.argv[1]:
            daemon.mms_email_poll_job()
        else:
            print "Unknown command"
            sys.exit(2)
            sys.exit(0)
    else:
        print "usage: %s start|stop|restart|run|runonce" % sys.argv[0]
        sys.exit(2)
