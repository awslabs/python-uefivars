#!/usr/bin/env python3
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT

import argparse
import sys
from uefivars import *

def Str2UEFIVarStore(s):
    if s == 'aws':
        return AWSUEFIVarStore
    elif s == 'edk2':
        return EDK2UEFIVarStore
    elif s == 'json':
        return JSONUEFIVarStore
    else:
        raise('Unknown Input type "%s", choose from ("aws, "json")' % s)

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help='Input type ("aws", "json")', required=True)
parser.add_argument("-o", "--output", help='Output type ("aws", "json")', required=True)
parser.add_argument("-I", "--inputfile", help='Input file (stdin if not given)')
parser.add_argument("-O", "--outputfile", help='Output file (stdout if not given)')
args = parser.parse_args()

if args.inputfile:
    infile = open(args.inputfile, "rb")
else:
    infile = sys.stdin.buffer
indata = infile.read()

inclass = Str2UEFIVarStore(args.input)
outclass = Str2UEFIVarStore(args.output)

varstore = inclass(indata)
varstore.__class__ = outclass

if args.outputfile:
    outfile = open(args.outputfile, "wb")
else:
    outfile = sys.stdout.buffer
outfile.write(bytes(varstore))
