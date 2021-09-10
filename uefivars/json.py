#!/usr/bin/env python3
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT

import base64
import json
import uuid
from .varstore import *

class JSONVar(UEFIVar):
    def __init__(self, jvar):
        var = {}
        name = jvar['name']
        data = base64.b64decode(jvar['data'])
        guid = uuid.UUID(jvar['guid']).bytes_le
        attr = int(jvar['attr'])
        timestamp = None
        digest = None
        if 'timestamp' in jvar:
            timestamp = bytes.fromhex(jvar['timestamp'])
        if 'digest' in jvar:
            digest = bytes.fromhex(jvar['digest'])
        super().__init__(name, data, guid, attr, timestamp, digest)

    def __dict__(self):
        super().__dict__()

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bytes):
            return " ".join("{0:02x}".format(c) for c in o)
        try:
            return json.JSONEncoder.default(self, o)
        except:
            return o.__dict__()

class JSONUEFIVarStore(UEFIVarStore):
    def __init__(self, data):
        super().__init__()

        # Read the JSON file
        jsondec = json.JSONDecoder()
        jdata = jsondec.decode(data.decode('utf-8'))

        # Copy all JSON elements to the store
        for jvar in jdata:
            self.vars.append(JSONVar(jvar))

    def __bytes__(self):
        return self.__str__().encode('utf-8')

    def prepare(self, var):
        var.data = base64.b64encode(var.data).decode('ascii')
        var.guid = str(uuid.UUID(bytes_le=var.guid))
        return var

    def __str__(self):
        vars = list(map(self.prepare, self.vars))
        jsonenc = JSONEncoder(indent=4, separators=(',', ': '))
        return jsonenc.encode(vars)
