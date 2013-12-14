#!/usr/bin/python
import os, sys
import token_parser

for line in sys.stdin:
#    item=line.strip().split()
    if token_parser.isEntity(line[0]):
        print line.strip()
