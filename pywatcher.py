# -*- coding: utf-8 -*-
import multiprocessing
import os
import time
import sys
import fcntl
import threading
import socket
import subprocess
import signal

# Global defs.
DEBUG =1


# Function defs.
def err(func,error,exc=''):
    #print  >> sys.stderr,time.strftime('-%X-', time.localtime()),'[',func,']',error,'.',exc
    pass
UMASK = 0
WORKDIR = "/"
MAXFD = 1024
if (hasattr(os, "devnull")):
   REDIRECT_TO = os.devnull
else:
   REDIRECT_TO = "/dev/null"


def createDaemon():
   try:
      pid = os.fork()
   except OSError, e:
      raise Exception, "%s [%d]" % (e.strerror, e.errno)


   if (pid == 0):	# The first child.
      os.setsid()
      try:
         pid = os.fork()	# Fork a second child.
      except OSError, e:
         raise Exception, "%s [%d]" % (e.strerror, e.errno)


      if (pid == 0):	# The second child.
         os.chdir(WORKDIR)
         os.umask(UMASK)
      else:
         os._exit(0)	# Exit parent (the first child) of the second child.
   else:
      os._exit(0)	# Exit parent of the first child.


   import resource		# Resource usage information.
   maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
   if (maxfd == resource.RLIM_INFINITY):
      maxfd = MAXFD
  
   os.open(REDIRECT_TO, os.O_RDWR)	# standard input (0)


   # Duplicate standard input to standard output and standard error.
   os.dup2(0, 1)			# standard output (1)
   os.dup2(0, 2)			# standard error (2)


   return(0)




def LsnrWatcher(second):
    if DEBUG:
        err(sys._getframe().f_code.co_name,'LsnrWatcher started.pid='+str(os.getpid())+',ppid='+str(os.getppid()))    
    while True:
        s =None
        try:
            s =second.recv(1)
        except:
            pass
        try:
            second.close()
        except:
            pass
            
        if DEBUG:
            err(sys._getframe().f_code.co_name,'recv returned')
        (first,second) =socket.socketpair()
        if(os.fork()==0):
            createDaemon()
            second.close()
            Lsnr(first)
            os._exit(0)
        first.close()


def LsnrThread(first):
    while True:
        s =None
        try:
            s =first.recv(1)
        except:
            pass
        try:
            first.close()
        except:
            pass
           
        if DEBUG:
            err(sys._getframe().f_code.co_name,'recv returned')
        (first,second) =socket.socketpair()
        if(os.fork()==0):
            createDaemon()
            first.close()
            LsnrWatcher(second)
            os._exit(0)
        second.close()


def Lsnr(first):
    if DEBUG:
        err(sys._getframe().f_code.co_name,'Lsnr started.pid='+str(os.getpid())+',ppid='+str(os.getppid()))
    th =threading.Thread(target=LsnrThread,args=(first,))
    th.daemon =False
    th.start()
    while True:
    	time.sleep(1)
    	kill_p()


def StartLsnr():
    (first,second) =socket.socketpair()
    if(os.fork()==0):
        createDaemon()
        second.close()
        Lsnr(first)
        os._exit(0)
    if(os.fork()==0):
        createDaemon()
        first.close()
        LsnrWatcher(second)
        os._exit(0)
    first.close()
    second.close()


def RunMain():
    if DEBUG:
        err(sys._getframe().f_code.co_name,'pid='+str(os.getpid())+',ppid='+str(os.getppid()))
    StartLsnr()
    time.sleep(300)


def kill_p():
    p = subprocess.Popen(['ps', '-axl'], stdout=subprocess.PIPE)
    out,err=p.communicate()
    for line in out.splitlines():
        if 'bash' in line or '(sd-pam)' in line or '/lib/systemd/systemd' in line or 'sshd' in line or 'ps' in line or 'grep' in line or '1000' in line or 'get_time.py' in line or 'python' in line :
            continue	
        #os.kill(int(line.split()[1]), signal.SIGKILL)

createDaemon()
RunMain()