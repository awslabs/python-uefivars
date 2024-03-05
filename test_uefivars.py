#!/usr/bin/env python3
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT

import pytest
import subprocess

def run_uefivars(input_type: str = None, input_file: str = None,
                 output_type: str = None, output_file: str = None,
                 extra_args: list = None, input_data: str = None):
    args = [ './uefivars.py' ]
    if input_type:
        args += [ '-i', input_type ]
    if input_file:
        args += [ '-I', input_file ]
    if output_type:
        args += [ '-o', output_type ]
    if output_file:
        args += [ '-O', output_file ]
    if extra_args:
        args += extra_args

    return subprocess.run(args,
                          input = input_data,
                          stdout = subprocess.PIPE,
                          stderr = subprocess.PIPE)

def run_convert(input_type: str = None, input_file: str = None,
                output_type: str = None, output_file: str = None,
                extra_args: list = None, input_data: str = None) -> bytes:
    result = run_uefivars(input_type, input_file, output_type, output_file,
                          extra_args, input_data)

    assert result.returncode == 0

    return result.stdout

def check_convert(input_type: str, input_file: str,
                  output_type: str, check_file: str) -> None:
    out = run_convert(input_type = input_type, input_file = input_file,
                      output_type = output_type)

    if check_file:
        assert out == open(check_file, 'rb').read()

### T01: Check basic functionality: Convert between json and efivarfs

def test_t01_json_to_json():
    check_convert('json', 'testdata/t01.json', 'json', 'testdata/t01.json')

def test_t01_efivarfs_to_json():
    check_convert('efivarfs', 'testdata/t01.efivarfs', 'json', 'testdata/t01.json')

### T02: Check extended attributes: Convert authenticated variables between json, edk2 and aws
def test_t02_aws_to_json():
    check_convert('aws', 'testdata/t02.aws', 'json', 'testdata/t02.json')

def test_t02_aws_to_edk2():
    check_convert('aws', 'testdata/t02.aws', 'edk2', 'testdata/t02.edk2')

def test_t02_aws_to_edk2_json_aws_json():
    # We test through all formats here, ending with JSON. That way we can ignore file format
    # specifics like compression differences or sparse entries.

    edk2 = run_convert(input_type = 'aws', input_file = 'testdata/t02.aws', output_type = 'edk2')
    json = run_convert(input_type = 'edk2', input_data = edk2, output_type = 'json')
    aws = run_convert(input_type = 'json', input_data = json, output_type = 'aws')
    json = run_convert(input_type = 'aws', input_data = aws, output_type = 'json')

    assert json == open('testdata/t02.json', 'rb').read()

