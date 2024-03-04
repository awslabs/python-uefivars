#!/usr/bin/env python3
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT

import os
from .varstore import *
import uuid

class EFIVARFSUEFIVarStore(UEFIVarStore):
    """
    Varstore class to ingest an efivarfs directory as UEFI variables.

    Please beware that efivarfs only exposes UEFI variables that execute
    at runtime, so any boot time variables are unavailable. Also, additional
    metadata such as secure variable details are not readable through efivarfs.
    """

    def __init__(self, path):
        super().__init__()
        self.is_empty = False

        if not path:
            path = '/sys/firmware/efi/efivars'

        if not os.path.isdir(path):
            raise Exception(f'"{path}" is not a valid efivarfs path')

        var_names = os.listdir(path)
        # example:  'X-Nitro-BootServicesExited-8be4df61-93ca-11d2-aa0d-00e098032b8c'

        for var_name in var_names:
            # efivarfs file name are f'{name}-{guid}'
            s = var_name.split('-')

            try:
                # The last 5 elements make up the GUID
                guid = uuid.UUID('-'.join(s[-5:])).bytes_le
            except ValueError:
                raise Exception(f'Invalid efivarfs file "{var_name}"')

            # Anything before that is the name of the variable
            name = '-'.join(s[:-5])

            # efivarfs file contents are f'{attr.le32}{data}'
            content = open(os.path.join(path, var_name), 'rb').read()
            data = content[4:]
            attr = int.from_bytes(content[:4], "little")

            # Now that we reassembled everything, remember the variable
            self.vars.append(UEFIVar(name, data, guid, attr))

    def __str__(self) -> str:
        raise Exception('Unable to serialize efivarfs into a file')
