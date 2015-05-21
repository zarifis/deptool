#!/usr/bin/python
import subprocess, re, sys, copy, json, argparse
from pprint import pprint
import deptree

parser = argparse.ArgumentParser(description='Check the parent of a resource given its tree')
parser.add_argument('deptree', help='Dependency Tree to use for lookup')
parser.add_argument('uri', help='Target URI')
args = parser.parse_args()
with open(args.deptree) as f:
  d = json.load(f)
print(d[args.uri])
