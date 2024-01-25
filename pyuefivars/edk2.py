#!/usr/bin/env python3
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT

import struct
import tempfile
import os
from .aws_file import *
from .varstore import *

class EDK2Cert(object):
    def __init__(self, name: str, guid: bytes, digest: bytes):
        self.name = name
        self.guid = guid
        self.digest = digest

class EDK2CertDB(object):
    GUID_CERTDB = b'\x6e\xe5\xbe\xd9\xdc\x75\xd9\x49\xb4\xd7\xb5\x34\x21\x0f\x63\x7a'

    def __init__(self, uefivar: UEFIVar = None):
        self.certs = []
        if uefivar != None:
            self.init_from_var(uefivar)

    def init_from_var(self, uefivar: UEFIVar):
        file = tempfile.SpooledTemporaryFile()
        file.write(uefivar.data)
        file.seek(0, os.SEEK_SET)
        file = AWSVarStoreFile(file)
        size = file.read32()
        if size != len(uefivar.data):
            raise Exception("Invalid certdb length")
        size = size - 4

        while size != 0:
            guid = file.readguid()
            cert_node_size = file.read32()
            name_size = file.read32() * 2
            digest_size = file.read32()
            name = file.read(name_size).decode('utf-16le').rstrip('\0')
            digest = file.read(digest_size)
            self.certs.append(EDK2Cert(name, guid, digest))
            size = size - (16 + 4 + 4 + 4 + name_size + digest_size)

    def to_var(self, vars: UEFIVar):
        file = tempfile.SpooledTemporaryFile()
        file = AWSVarStoreFile(file)
        file.write32(0) # file size, gets patched in later
        pubkeyidx = 0
        for var in vars:
            if not var.digest:
                continue
            name_size = len(var.name) + 1
            digest_size = len(var.digest)
            file.writeguid(var.guid)
            file.write32(16 + 4 + 4 + 4 + name_size + digest_size)
            file.write32(name_size)
            file.write32(digest_size)
            file.write(var.name.encode('utf-16le') + b'\0\0')
            file.write(var.digest)
            var.pubkeyidx = pubkeyidx
            pubkeyidx = pubkeyidx + 1
        filesize = file.file.tell()
        file.file.seek(0, os.SEEK_SET)
        file.write32(filesize)
        file.file.seek(0, os.SEEK_SET)
        data = file.file.read()
        return UEFIVar("certdb", data, self.GUID_CERTDB, 0x7)

class EDK2UEFIVarStore(UEFIVarStore):
    GUID_CERTDB = b'\x6e\xe5\xbe\xd9\xdc\x75\xd9\x49\xb4\xd7\xb5\x34\x21\x0f\x63\x7a'
    GUID_NVFS = b'\x8d\x2b\xf1\xff\x96\x76\x8b\x4c\xa9\x85\x27\x47\x07\x5b\x4f\x50'
    GUID_VARSTORE = b'\x78\x2c\xf3\xaa\x7b\x94\x9a\x43\xa1\x80\x2e\x14\x4e\xc3\x77\x92'
    STATE_SETTLED = 0x3f
    VARSTORE_STATUS = b'\x5a\xfe\x00\x00\x00\x00\x00\x00'
    DEFAULT_LENGTH = 540672
    HEADER_LENGTH = 0x48
    EFI_FVB2_READ_DISABLED_CAP  = 0x00000001
    EFI_FVB2_READ_ENABLED_CAP   = 0x00000002
    EFI_FVB2_READ_STATUS        = 0x00000004
    EFI_FVB2_WRITE_DISABLED_CAP = 0x00000008
    EFI_FVB2_WRITE_ENABLED_CAP  = 0x00000010
    EFI_FVB2_WRITE_STATUS       = 0x00000020
    EFI_FVB2_LOCK_CAP           = 0x00000040
    EFI_FVB2_LOCK_STATUS        = 0x00000080
    EFI_FVB2_STICKY_WRITE       = 0x00000200
    EFI_FVB2_MEMORY_MAPPED      = 0x00000400
    EFI_FVB2_ERASE_POLARITY     = 0x00000800
    EFI_FVB2_READ_LOCK_CAP      = 0x00001000
    EFI_FVB2_READ_LOCK_STATUS   = 0x00002000
    EFI_FVB2_WRITE_LOCK_CAP     = 0x00004000
    EFI_FVB2_WRITE_LOCK_STATUS  = 0x00008000
    EFI_FVB2_ALIGNMENT          = 0x001F0000
    EFI_FVB2_WEAK_ALIGNMENT     = 0x80000000
    EFI_FVB2_ALIGNMENT_1        = 0x00000000
    EFI_FVB2_ALIGNMENT_2        = 0x00010000
    EFI_FVB2_ALIGNMENT_4        = 0x00020000
    EFI_FVB2_ALIGNMENT_8        = 0x00030000
    EFI_FVB2_ALIGNMENT_16       = 0x00040000
    EFI_FVB2_ALIGNMENT_32       = 0x00050000
    EFI_FVB2_ALIGNMENT_64       = 0x00060000
    EFI_FVB2_ALIGNMENT_128      = 0x00070000
    EFI_FVB2_ALIGNMENT_256      = 0x00080000
    EFI_FVB2_ALIGNMENT_512      = 0x00090000
    EFI_FVB2_ALIGNMENT_1K       = 0x000A0000
    EFI_FVB2_ALIGNMENT_2K       = 0x000B0000
    EFI_FVB2_ALIGNMENT_4K       = 0x000C0000
    EFI_FVB2_ALIGNMENT_8K       = 0x000D0000
    EFI_FVB2_ALIGNMENT_16K      = 0x000E0000
    EFI_FVB2_ALIGNMENT_32K      = 0x000F0000
    EFI_FVB2_ALIGNMENT_64K      = 0x00100000
    EFI_FVB2_ALIGNMENT_128K     = 0x00110000
    EFI_FVB2_ALIGNMENT_256K     = 0x00120000
    EFI_FVB2_ALIGNMENT_512K     = 0x00130000
    EFI_FVB2_ALIGNMENT_1M       = 0x00140000
    EFI_FVB2_ALIGNMENT_2M       = 0x00150000
    EFI_FVB2_ALIGNMENT_4M       = 0x00160000
    EFI_FVB2_ALIGNMENT_8M       = 0x00170000
    EFI_FVB2_ALIGNMENT_16M      = 0x00180000
    EFI_FVB2_ALIGNMENT_32M      = 0x00190000
    EFI_FVB2_ALIGNMENT_64M      = 0x001A0000
    EFI_FVB2_ALIGNMENT_128M     = 0x001B0000
    EFI_FVB2_ALIGNMENT_256M     = 0x001C0000
    EFI_FVB2_ALIGNMENT_512M     = 0x001D0000
    EFI_FVB2_ALIGNMENT_1G       = 0x001E0000
    EFI_FVB2_ALIGNMENT_2G       = 0x001F0000

    def __init__(self, data):
        super().__init__()

        self.certdb = EDK2CertDB()

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
        if fsguid != self.GUID_NVFS:
            raise Exception("Invalid GUID: %s" % fsguid)

        self.length = file.read64()
        if self.length > len(data):
            raise Exception("Invalid length: %s" % self.length)

        sig = file.read(4)
        if sig != b'_FVH':
            raise Exception('Invalid FVH signature: %s' % sig)

        self.attrs = file.read32()

        hlength = file.read16()
        if hlength != self.HEADER_LENGTH:
            raise Exception('Invalid FVH Header Length: 0x%x' % hlength)

        csum_hdr = file.read16()
        if (self.csum16(data[:self.HEADER_LENGTH]) != 0):
            raise Exception("Invalid header checksum: 0x%x" % csum_hdr)
        file.read(3)
        rev = file.read8()
        if rev != 0x2:
            raise Exception('Invalid FVH Revision: 0x%x' % rev)

        file.read(0x10)
        vsguid = file.readguid()
        if vsguid != self.GUID_VARSTORE:
            raise Exception('Invalid Varstore GUID: %s' % vsguid)

        self.varsize = file.read32()
        status = file.read(8)
        if status != self.VARSTORE_STATUS:
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
            if state == self.STATE_SETTLED:
                if timestamp == self.EMPTY_TIMESTAMP:
                    timestamp = None
                var = UEFIVar(name, data, guid, attr, timestamp, None)
                if name == "certdb" and guid == self.GUID_CERTDB:
                    self.certdb = EDK2CertDB(var)
                else:
                    self.vars.append(var)
            file.file.seek((file.file.tell() + 0x3) & ~0x3, os.SEEK_SET)

        # Extract all certdb entries into digest fields
        for cert in self.certdb.certs:
            for var in self.vars:
                if var.name == cert.name and var.guid == cert.guid:
                    var.digest = cert.digest

    def csum16(self, var : bytes):
        u16 = struct.unpack("<" + str(int(len(var) / 2)) + "H", var)
        csum = 0
        for b in u16:
            #print("0x%x + 0x%x = 0x%x" % (csum, b, csum + b))
            csum = csum + b
        return (csum & 0xffff)

    def write_var(self, raw : AWSVarStoreFile, var : UEFIVar):
        raw.write16(0x55aa)
        raw.write8(self.STATE_SETTLED)
        raw.write8(0)
        raw.write32(var.attr)
        raw.write64(0) # monotonic count
        if var.timestamp:
            raw.write(var.timestamp)
        else:
            raw.write(b'\0' * 16)
        if hasattr(var, 'pubkeyidx'):
            raw.write32(var.pubkeyidx)
        else:
            raw.write32(0)
        raw.write32(len(var.name + '\0') * 2)
        raw.write32(len(var.data))
        raw.write(var.guid)
        raw.write((var.name + '\0').encode('utf-16le'))
        raw.write(var.data)
        raw.file.seek((raw.file.tell() + 0x3) & ~0x3, os.SEEK_SET)

    def __bytes__(self) -> bytes:
        if not hasattr(self, 'certdb'):
            self.certdb = EDK2CertDB()
        if not hasattr(self, 'length'):
            self.length = self.DEFAULT_LENGTH
        if not hasattr(self, 'attrs'):
            self.attrs = self.EFI_FVB2_READ_DISABLED_CAP  | \
                         self.EFI_FVB2_READ_ENABLED_CAP   | \
                         self.EFI_FVB2_READ_STATUS        | \
                         self.EFI_FVB2_WRITE_DISABLED_CAP | \
                         self.EFI_FVB2_WRITE_ENABLED_CAP  | \
                         self.EFI_FVB2_WRITE_STATUS       | \
                         self.EFI_FVB2_LOCK_CAP           | \
                         self.EFI_FVB2_LOCK_STATUS        | \
                         self.EFI_FVB2_STICKY_WRITE       | \
                         self.EFI_FVB2_MEMORY_MAPPED      | \
                         self.EFI_FVB2_ERASE_POLARITY     | \
                         self.EFI_FVB2_READ_LOCK_CAP      | \
                         self.EFI_FVB2_READ_LOCK_STATUS   | \
                         self.EFI_FVB2_WRITE_LOCK_CAP     | \
                         self.EFI_FVB2_WRITE_LOCK_STATUS  | \
                         self.EFI_FVB2_ALIGNMENT_16
        if not hasattr(self, 'varsize'):
            self.varsize = int(self.length / 2) - 8264

        # Assemble the flash file
        raw = AWSVarStoreFile(tempfile.SpooledTemporaryFile())
        raw.write(b'\0' * 16)
        raw.write(self.GUID_NVFS)
        raw.write64(self.length)
        raw.write(b'_FVH')
        raw.write32(self.attrs)
        raw.write16(self.HEADER_LENGTH)
        csum_pos = raw.file.tell()
        raw.write16(0) # checksum - need to fill in later
        raw.write(b'\0' * 3)
        raw.write8(0x2) # revision
        raw.write(b'\x84\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        raw.write(self.GUID_VARSTORE)
        raw.write32(self.varsize)
        raw.write(self.VARSTORE_STATUS)
        header_end_pos = raw.file.tell()

        self.write_var(raw, self.certdb.to_var(self.vars))

        for var in self.vars:
            self.write_var(raw, var)

        if raw.file.tell() > self.length:
            raise Exception("Can not fit variables into store")

        # Expand to maximum file size
        raw.file.seek(self.length - 1, os.SEEK_SET)
        raw.write8(0)

        # Calculate checksums
        raw.file.seek(0, os.SEEK_SET)
        full = raw.file.read()
        raw.file.seek(csum_pos, os.SEEK_SET)
        raw.write16((0x10000 - self.csum16(full[:self.HEADER_LENGTH])) & 0xffff)

        raw.file.seek(0, os.SEEK_SET)
        return raw.file.read()

    def set_output_options(self, options):
        for option in [option.strip().split("=") for option in options]:
            if option[0] == 'filesize':
                if(len(option) != 2 or not option[1]):
                    raise SystemExit(
                        'option "filesize" requires a second argument'
                    )
                self.length = int(option[1]) * 1024
            else:
                raise SystemExit(
                    'Unknown Option type "{}"'.format(option)
                )
