# coding: utf-8
import random
import time

WAIT_TIME_DEF = 3
WAIT_TIME_MAX = 10

def stop(second=WAIT_TIME_MAX):
    
    global WAIT_TIME_DEF
    try:
        time.sleep(int(second))
    except:
        time.sleep(WAIT_TIME_DEF)

def stop_random(min, max):
    
    global WAIT_TIME_DEF,WAIT_TIME_MAX
    w1 = WAIT_TIME_DEF
    w2 = WAIT_TIME_MAX
    try:
        if min:
            w1 = min
    except:
        pass

    try:
        if max:
            w2 = max
    except:
        pass
    
    second = random.randint(w1,w2)
    time.sleep(int(second))

