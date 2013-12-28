#!/usr/bin/python
import os, sys

def turn_to_data():
    for line in sys.stdin:
        items=line.strip().split()
        if len(items)==2:
            print '\n'.join([items[0] for i in range(int(items[1]))])

if __name__=='__main__':
    turn_to_data()
