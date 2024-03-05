#!/usr/bin/env python3
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT

import sys


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
        if self.timestamp is not None:
            var['timestamp'] = self.timestamp
        if self.digest is not None:
            var['digest'] = self.digest

        return var


class UEFIVarStore(object):
    EMPTY_TIMESTAMP = b'\0' * 16
    EMPTY_DIGEST = b'\0' * 32

    def __init__(self, data=''):
        self.vars = []

    def __dict__(self):
        return self.vars

    def __bytes__(self):
        print("This output backend does not implement writing the variable store", file=sys.stderr)
        sys.exit()

    def set_output_options(self, options):
        print("This output backend does not implement output options: {}".format(options), file=sys.stderr)
        sys.exit()
