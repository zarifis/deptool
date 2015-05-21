#!/usr/bin/python
import subprocess, re, sys, copy, json, argparse
from pprint import pprint
import deptree

parser = argparse.ArgumentParser(description='Get a current dependency tree for a page')
parser.add_argument('target', help='Target URL')
parser.add_argument('ua', help='User Agent (chrome|firefox|ie10|ie9|opera|safari-ipad|safari-mac)')
args = parser.parse_args()

url = args.target
ua = args.ua

#print 'Inferred Dependency Tree:'
depTree = deptree.get_dep_tree(url, ua)
print json.dumps(depTree, sort_keys=True, indent=2)

