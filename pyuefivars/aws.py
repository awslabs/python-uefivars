#!/usr/bin/env python3
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT

import os
import zlib
import base64
import tempfile
import google_crc32c as crc32c
from .varstore import UEFIVar, UEFIVarStore
from .aws_v0 import UEFIVarStoreV0
from .aws_file import AWSVarStoreFile


class AWSUEFIVarStore(UEFIVarStore):
    EFI_VARIABLE_TIME_BASED_AUTHENTICATED_WRITE_ACCESS = 0x20
    AMZNUEFI = 0x494645554e5a4d41

    def __init__(self, b64data: bytes):
        super().__init__()

        # Convert base64 to binary
        file = tempfile.SpooledTemporaryFile()
        file.write(base64.b64decode(b64data))
        file.seek(0, os.SEEK_SET)

        # Then wrap the binary file with our reader and start parsing
        file = AWSVarStoreFile(file)
        magic = file.read64()
        if magic != self.AMZNUEFI:
            raise Exception("Invalid magic. Expected AMZNUEFI. Found 0x%x" % magic)
        crc32 = file.read32()

        # Validate crc32c
        location = file.file.tell()
        comp_crc32 = crc32c.value(file.readall())
        if (comp_crc32 != crc32):
            raise Exception("Invalid checksum, please check you copied all data")
        file.file.seek(location, os.SEEK_SET)

        version = file.read32()
        if version != 0:
            raise Exception("Invalid version. Expected 0. Found 0x%x" % version)

        # Grab the zlib data that's embedded and parse it
        dec = zlib.decompressobj(0, zdict=UEFIVarStoreV0.dict)
        raw_data = dec.decompress(file.readall())
        raw_file = tempfile.SpooledTemporaryFile()
        raw_file.write(raw_data)
        raw_file.seek(0, os.SEEK_SET)
        raw = AWSVarStoreFile(raw_file)
        nr_entries = raw.read64()
        for i in range(nr_entries):
            name = raw.readstr()
            data = raw.readdata()
            guid = raw.readguid()
            attr = raw.read32()
            if attr & self.EFI_VARIABLE_TIME_BASED_AUTHENTICATED_WRITE_ACCESS:
                timestamp = raw.readtimestamp()
                if timestamp == self.EMPTY_TIMESTAMP:
                    timestamp = None
                digest = raw.readdata()
                if digest == self.EMPTY_DIGEST:
                    digest = None
                self.vars.append(UEFIVar(name, data, guid, attr, timestamp, digest))
            else:
                self.vars.append(UEFIVar(name, data, guid, attr))

    def __bytes__(self) -> bytes:
        # Assemble the zlib compressed wrapped file
        raw = AWSVarStoreFile(tempfile.SpooledTemporaryFile())
        raw.write64(len(self.vars))
        for var in self.vars:
            raw.writestr(var.name)
            raw.writedata(var.data)
            raw.writeguid(var.guid)
            raw.write32(var.attr)
            if var.attr & self.EFI_VARIABLE_TIME_BASED_AUTHENTICATED_WRITE_ACCESS:
                timestamp = var.timestamp
                if timestamp is None:
                    timestamp = self.EMPTY_TIMESTAMP

                digest = var.digest
                if digest is None:
                    digest = self.EMPTY_DIGEST

                raw.writetimestamp(timestamp)
                raw.writedata(digest)
        raw.file.seek(0, os.SEEK_SET)

        enc = zlib.compressobj(9, zdict=UEFIVarStoreV0.dict)
        zdata = enc.compress(raw.file.read()) + enc.flush()

        # Create a full file with header + zdata
        f = tempfile.SpooledTemporaryFile()
        f = AWSVarStoreFile(f)
        f.write64(self.AMZNUEFI)
        f.write32(crc32c.value(int(0).to_bytes(4, byteorder='little') + zdata))
        f.write32(0)  # Version 0
        f.write(zdata)
        f.file.seek(0, os.SEEK_SET)

        # Then write it out as base64 data
        return base64.b64encode(f.file.read())

    def __str__(self) -> str:
        return self.__bytes__().decode('utf-8')
