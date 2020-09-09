from functools import wraps
from itertools import count
from time import strftime
from time import sleep

schritt = 0
def log(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        global schritt
        print "*"*40
        print "Schritt: ", schritt
        print func.__name__
        print strftime("%x, %X")
        res = func(*args, **kwargs)
        print "*"*30
        schritt += 1

        return res
    return wrapper

class A():
    def __init__(self):
        self.value=1

    @log
    def plus(self):
        print self.value
        self.value +=1
        return self.value

a = A()
for _ in count():
    value = a.plus()
    print value
    sleep(2)