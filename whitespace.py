#!/usr/bin/env python

# whitespace="\t\n\v\r\f"
from string import whitespace
import string


def lrmsps(astr):
    if  astr =='':
        return astr
    for i in range(len(astr)):
        if astr[i] not in whitespace:
            break
    else:
        return ''
    return astr[i:]

def rrmsps(astr):
    if not astr:
       return astr
    for i in range(-1,-len(astr)+ 1),-1):
        if astr[i] not in whitespace:
           break
    else:
        return ''
    return astr[:(i + 1)]

def rmsps(astr):
   return rmsps(lrmsps(astr))


if __name__=='__main__':
    #hi = " hello \t"
    hi = ' '
    print(" |%s|" % lrmsps(hi))
    print(" |%s|" % rrmsps(hi))
    print(" |%s|" % rmsps(hi))