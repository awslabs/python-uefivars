#!/usr/bin/env python3
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT

import tempfile
import os
from .aws_file import *
from .varstore import *

class EDK2UEFIVarStore(UEFIVarStore):
    def __init__(self, data):
        super().__init__()

        # Get a streaming file object
        file = tempfile.SpooledTemporaryFile()
        file.write(data)
        file.seek(0, os.SEEK_SET)
        file = AWSVarStoreFile(file)

        # Validate header
        zerovector = file.read(0x10)
        if zerovector != b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0':
            raise Exception("Invalid Zero Vector: %s" % zerovector)

        fsguid = file.readguid()
        if fsguid != b'\x8d\x2b\xf1\xff\x96\x76\x8b\x4c\xa9\x85\x27\x47\x07\x5b\x4f\x50':
            raise Exception("Invalid GUID: %s" % fsguid)

        self.length = file.read64()

        sig = file.read(4)
        if sig != b'_FVH':
            raise Exception('Invalid FVH signature: %s' % sig)

        self.attrs = file.read32()

        hlength = file.read16()
        if hlength != 0x48:
            raise Exception('Invalid FVH Header Length: 0x%x' % hlength)

        csum = file.read16()
        file.read(3)
        rev = file.read8()
        if rev != 0x2:
            raise Exception('Invalid FVH Revision: 0x%x' % rev)

        file.read(0x10)
        vsguid = file.readguid()
        if vsguid != b'\x78\x2c\xf3\xaa\x7b\x94\x9a\x43\xa1\x80\x2e\x14\x4e\xc3\x77\x92':
            raise Exception('Invalid Varstore GUID: %s' % vsguid)

        self.varsize = file.read32()
        status = file.read(8)
        if status != b'\x5a\xfe\x00\x00\x00\x00\x00\x00':
            raise Exception('Invalid Varstore Status: %s' % status)

        # Extract all variables
        while file.read16() == 0x55aa:
            state = file.read8()
            file.read8()
            attr = file.read32()
            monotoniccount = file.read64()
            timestamp = file.readtimestamp()
            pubkeyidx = file.read32()
            namelen = file.read32()
            datalen = file.read32()
            guid = file.readguid()
            name = file.read(namelen).decode('utf-16le').rstrip('\0')
            data = file.read(datalen)
            if state == 0x3f:
                self.vars.append(UEFIVar(name, data, guid, attr, timestamp, bytes(pubkeyidx)))
            file.file.seek((file.file.tell() + 0x3) & ~0x3, os.SEEK_SET)
