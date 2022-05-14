#!/usr/bin/env python3
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT

import json
import uuid
from .varstore import *

class JSONVar(UEFIVar):
    def __init__(self, jvar):
        var = {}
        name = jvar['name']
        data = bytes.fromhex(jvar['data'])
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

class JSONUEFIVarStore(UEFIVarStore):
    current_version = 2

    def __init__(self, data):
        super().__init__()

        # Read the JSON file
        jdata = json.loads(data.decode('utf-8'))
        vardata = []
        if isinstance(jdata, list):
            self.version = 1
            vardata = jdata
        else:
            self.version = jdata.get('version', self.current_version)
            vardata = jdata.get('variables', [])

        if self.version > self.current_version:
            raise SystemExit(
                'Unknown Version "{}", this tool only supports up to version "{}"'.format(self.version, self.current_version)
            )

        # Copy all JSON elements to the UEFIVars for the store
        for jvar in vardata:
            new_var = JSONVar(jvar)
            new_var.__class__ = UEFIVar
            self.vars.append(new_var)

    def __bytes__(self):
        return self.__str__().encode('utf-8')

    def prepare(self, var):
        new_var = var.__dict__()

        if 'guid' in new_var:
             new_var["guid"] = str(uuid.UUID(bytes_le=var.guid))

        for key in new_var:
            if isinstance(new_var[key], bytes):
                new_var[key] = new_var[key].hex()

        return new_var

    def __str__(self):
        encoded_vars = list(map(self.prepare, self.vars))
        store = {
            "version": self.current_version,
            "variables": encoded_vars,
        }
        return json.dumps(store, indent=4)
