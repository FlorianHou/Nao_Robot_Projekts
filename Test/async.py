import qi
import functools
import time

def doSomeWork():
  #do your work here instead of sleeping
    global i
    i += 1
    print "func", i

i = 0

Per = qi.PeriodicTask()
Per.setCallback(functools.partial(doSomeWork,))
Per.setUsPeriod(10000000)
Per.start(True)


while True:
    print i
    time.sleep(3)