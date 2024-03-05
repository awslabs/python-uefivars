# uefivars

This is a set of Python modules and a helper application "uefivars" to
introspect and modify UEFI variable stores.

## Why do I need this?

UEFI variable stores are typically opaque to users. You access them using
UEFI runtime services as function calls. However, the data is then stored
in a binary data format. When running virtual machines or extracting UEFI
variable stores directly from Flash storage, you can receive and write that
binary data and thus modify variables directly.

This is useful in situations where you have incorrect UEFI variable data
and need to modify variables without runtime service access. It can also
be useful to analyze and introspect the variable store and check what data
is stored inside.

## How do I use it?

You can convert a variable store into human readable format by setting the
output type to json. This will show you all variables that are currently
present in the variable store.

```console
$ uefivars -i edk2 -o json -I OVMF_VARS.secboot.fd
[
    {
        "name": "SecureBootEnable",
        "data": "AQ==",
        "guid": "f0a30bc7-af08-4556-99c4-001009c93a44",
        "attr": 3
    },
    [...]
]
```

In addition, you can convert from the human readable json representation back
into edk2 format:

```console
$ uefivars -i json -o edk2 -I vars.json -O OVMF_VARS.fd
```

Given any variable store (including an empty one) the `--PK` , `--KEK` , `--db` and `--dbx`
switches can be used to (over-)write the four SecureBoot variables from input files.
(Usually .esl files). For a general rundown of the key generation process the [ArchLinux](https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface/Secure_Boot#Creating_keys) wiki has proven itself
as a first point of guidance.

You can also use the tool to convert between the AWS EC2 uefi-data format
and edk2 to import and export UEFI variable stores between an EC2 instance
and QEMU:

```console
$ uefivars -i edk2 -o aws -I OVMF_VARS.fd -O uefi-data.aws
```

```console
$ uefivars -i aws -o edk2 -I uefi-data.aws -O OVMF_VARS.fd
```

## How can I take a snapshot of my current UEFI variable store?

If you are running on a live UEFI system, the variable store that gets exposed
to the Operating System is incomplete: It does not contain UEFI variables that
are only present at boot time and it does not get access to variable
authentication data.

If you don't need either - for example because you're only interested in saving
the boot order - you can use the efivarfs backend to convert the local variable
store into a file:

```console
$ uefivars -i efivarfs -o aws -I /sys/firmware/efi/efivars -O uefi-data.aws
```

## What formats are supported?

This package currently supports the following formats:

**aws** - File format used in [AWS EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/uefi-secure-boot.html) \
**edk2** - File format used for flash storage in [OVMF](https://github.com/tianocore/edk2/blob/918288ab5a7c3abe9c58d576ccc0ae32e2c7dea0/OvmfPkg/README#L123) \
**efivarfs** - Ingests all non-authenticated variables from an [efivarfs](https://docs.kernel.org/filesystems/efivarfs.html) mount point (read only)
