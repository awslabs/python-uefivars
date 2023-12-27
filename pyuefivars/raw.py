#!/usr/bin/env python3
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT

import os
from .varstore import *
import re
import uuid

GUID_RE = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}', re.I)


class RAWUEFIVarStore(UEFIVarStore):

    def __init__(self, dummy):
        super().__init__()
        del dummy
        self.is_empty = False
        if not os.path.isdir("/sys/firmware/efi") or not os.path.isdir('/sys/firmware/efi/efivars'):
            self.is_empty = True
            return

        var_names = os.listdir('/sys/firmware/efi/efivars')
        # example:  'X-Nitro-BootServicesExited-8be4df61-93ca-11d2-aa0d-00e098032b8c'

        for var_name in var_names:
            # print(f"working on variable {var_name}")
            res = GUID_RE.search(var_name)
            guid_str = var_name[res.span()[0]: res.span()[1]]
            guid = uuid.UUID(guid_str).bytes_le
            name = var_name[:res.span()[0] - 1]  # need to remove last "-" before GUID
            with open(os.path.join('/sys/firmware/efi/efivars', var_name), 'rb') as f:
                content = f.read()
            data = content[1:]
            attr = int.from_bytes(content[:1], "big")
            self.vars.append(UEFIVar(name, data, guid, attr))

    def __str__(self) -> str:
        return ""
