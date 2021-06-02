#!/usr/bin/env python3
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT

class UEFIVar(object):
    def __init__(self, name: str, data: bytes, guid: bytes, attr: int, timestamp: bytes = None, digest: bytes = None):
        self.name = name
        self.data = data
        self.guid = guid
        self.attr = attr
        self.timestamp = timestamp
        self.digest = digest

    def __dict__(self):
        var = {}
        var['name'] = self.name
        var['data'] = self.data
        var['guid'] = self.guid
        var['attr'] = self.attr
        if self.timestamp != None:
            var['timestamp'] = self.timestamp
        if self.digest != None:
            var['digest'] = self.digest

        return var

class UEFIVarStore(object):
    def __init__(self):
        self.vars = []

    def __dict__(self):
        return self.vars

    def __bytes__(self):
        raise("This backend does not implement writing the variable store")
