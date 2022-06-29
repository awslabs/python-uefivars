#!/usr/bin/env python3
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT

class AWSVarStoreFile(object):
    def __init__(self, file):
        self.file = file

    def read(self, size):
        value = self.file.read(size)
        if len(value) != size:
            raise Exception("Unexpected end of %s at 0x%x" % (self.file, self.file.tell()))
        return value

    def read64(self):
        return int.from_bytes(self.read(8), byteorder='little', signed=False)

    def read32(self):
        return int.from_bytes(self.read(4), byteorder='little', signed=False)

    def read16(self):
        return int.from_bytes(self.read(2), byteorder='little', signed=False)

    def read8(self):
        return int.from_bytes(self.read(1), byteorder='little', signed=False)

    def readdata(self):
        size = self.read64()
        return self.read(size)

    def readstr(self):
        return self.readdata().decode('utf-8')

    def readguid(self):
        return self.read(16)

    def readtimestamp(self):
        return self.read(16)

    def readall(self):
        return self.file.read()

    def write(self, data):
        self.file.write(data)

    def write64(self, data):
        self.write(data.to_bytes(8, byteorder='little'))

    def write32(self, data):
        self.write(data.to_bytes(4, byteorder='little'))

    def write16(self, data):
        self.write(data.to_bytes(2, byteorder='little'))

    def write8(self, data):
        self.write(data.to_bytes(1, byteorder='little'))

    def writedata(self, data):
        self.write64(len(data))
        self.write(data)

    def writestr(self, data):
        return self.writedata(data.encode('utf-8'))

    def writeguid(self, data):
        return self.write(data)

    def writetimestamp(self, data):
        return self.write(data)
