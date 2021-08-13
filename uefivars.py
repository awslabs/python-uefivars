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
        raise SystemExit(
            'Unknown Input type "{}", choose from ("aws, "json", "edk2")'.format(s)
        )

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help='Input type ("aws", "json", "edk2")', required=True)
parser.add_argument("-o", "--output", help='Output type ("aws", "json", "edk2")', required=True)
parser.add_argument("-I", "--inputfile", help='Input file (stdin if not given)')
parser.add_argument("-O", "--outputfile", help='Output file (stdout if not given)')
args = parser.parse_args()

inclass = Str2UEFIVarStore(args.input)
outclass = Str2UEFIVarStore(args.output)

if args.inputfile:
    infile = open(args.inputfile, "rb")
else:
    infile = sys.stdin.buffer
    print("Reading uefivars from stdin", file=sys.stderr)

indata = infile.read()

varstore = inclass(indata)
varstore.__class__ = outclass

if args.outputfile:
    outfile = open(args.outputfile, "wb")
else:
    outfile = sys.stdout.buffer
outfile.write(bytes(varstore))
