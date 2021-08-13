#!/usr/bin/env python3
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="uefivars",
    version="0.1",
    author="Amazon Web Services",
    author_email="graf@amazon.com",
    description="UEFI variable store tools",
    long_description=long_description,
    url="https://github.com/awslabs/python-uefivars",
    packages=setuptools.find_packages(),
    install_requires=[ 'crc32c' ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
