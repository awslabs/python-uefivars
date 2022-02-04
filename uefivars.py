#!/usr/bin/env python3
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT

import argparse
import sys
from uefivars import *

MIN_PYTHON = (3, 0)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

globalEfiGUID = bytes.fromhex("61 df e4 8b ca 93 d2 11 aa 0d 00 e0 98 03 2b 8c")
secureDatabaseGUID = bytes.fromhex("cb b2 19 d7 3a 3d 96 45 a3 bc da d0 0e 67 65 6f")

def Str2UEFIVarStore(s):
    if s == 'aws':
        return AWSUEFIVarStore
    elif s == 'edk2':
        return EDK2UEFIVarStore
    elif s == 'json':
        return JSONUEFIVarStore
    elif s == 'none':
        return UEFIVarStore
    else:
        raise SystemExit(
            'Unknown Input type "{}", choose from ("aws, "json", "edk2", "none")'.format(s)
        )

def ReadVar(arg, name, guid):
    EFI_VARIABLE_NON_VOLATILE=0x00000001
    EFI_VARIABLE_BOOTSERVICE_ACCESS=0x00000002
    EFI_VARIABLE_RUNTIME_ACCESS=0x00000004
    EFI_VARIABLE_TIME_BASED_AUTHENTICATED_WRITE_ACCESS=0x00000020

    attr = EFI_VARIABLE_NON_VOLATILE | EFI_VARIABLE_BOOTSERVICE_ACCESS | EFI_VARIABLE_RUNTIME_ACCESS | EFI_VARIABLE_TIME_BASED_AUTHENTICATED_WRITE_ACCESS

    varfile = open(arg, "rb")
    vardata = varfile.read()

    if(len(vardata) == 0):
        print('Read empty variable "{}". Aborting'.format(name), file=sys.stderr)
        sys.exit()

    return UEFIVar(name, vardata, guid, attr)

pk_found = -1
kek_found = -1
db_found = -1
dbx_found = -1

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help='Input type ("aws", "json", "edk2", "none")', required=True)
parser.add_argument("-o", "--output", help='Output type ("aws", "json", "edk2[,filesize=512]")', required=True)
parser.add_argument("-I", "--inputfile", help='Input file (stdin if not given)')
parser.add_argument("-O", "--outputfile", help='Output file (stdout if not given)')
parser.add_argument("-P", "--PK", help='Insert PK from given file (usually PK.esl)')
parser.add_argument("-K", "--KEK", help='Insert KEK from given file (usually KEK.esl)')
parser.add_argument("-b", "--db", help='Insert db from given file (usually db.esl)')
parser.add_argument("-x", "--dbx", help='Insert dbx from given file (usually dbx.esl)')

args = parser.parse_args()

inclass = Str2UEFIVarStore(args.input)

args.output = [s.strip() for s in args.output.split(",")]
output_options = args.output[1:]
args.output = args.output[0]

outclass = Str2UEFIVarStore(args.output)

if args.input == 'none':
    indata = ''
else:
    if args.inputfile:
        infile = open(args.inputfile, "rb")
    else:
        infile = sys.stdin.buffer
        print("Reading uefivars from stdin", file=sys.stderr)

    indata = infile.read()

varstore = inclass(indata)

print("Read {} variables".format(varstore.vars.__len__()), file=sys.stderr)

for i, s in enumerate(varstore.vars):
    var = varstore.vars[i]

    if (var.name == 'PK' and var.guid == globalEfiGUID):
        pk_found = i

    if (var.name == 'KEK' and var.guid == globalEfiGUID):
        kek_found = i

    if (var.name == 'db' and var.guid == secureDatabaseGUID):
        db_found = i

    if (var.name == 'dbx' and var.guid == secureDatabaseGUID):
        dbx_found = i

if (args.PK):
    var = ReadVar(args.PK, 'PK', globalEfiGUID)
    if (pk_found != -1):
        print('Replacing PK', file=sys.stderr)
        varstore.vars[pk_found] = var
    else:
        varstore.vars.append(var)
elif (pk_found == -1):
    print('No PK (PlatformKey) was set; SecureBoot will not be enabled without a PK', file=sys.stderr)

if (args.KEK):
    var =  ReadVar(args.KEK, 'KEK', globalEfiGUID)
    if (kek_found != -1):
        print('Replacing KEK', file=sys.stderr)
        varstore.vars[kek_found] = var
    else:
        varstore.vars.append(var)

if (args.db):
    var = ReadVar(args.db, 'db', secureDatabaseGUID)
    if (db_found != -1):
        print('Replacing db', file=sys.stderr)
        varstore.vars[db_found] = var
    else:
        varstore.vars.append(var)

if (args.dbx):
    var = ReadVar(args.dbx, 'dbx', secureDatabaseGUID)
    if (dbx_found != -1):
        print('Replacing dbx', file=sys.stderr)
        varstore.vars[dbx_found] = var
    else:
        varstore.vars.append(var)

# convert the format by changing the output class
varstore.__class__ = outclass
if output_options:
    varstore.set_output_options(output_options)

if args.outputfile:
    outfile = open(args.outputfile, "wb")
else:
    outfile = sys.stdout.buffer
outfile.write(bytes(varstore))

print("Writen {} variables".format(varstore.vars.__len__()), file=sys.stderr)
