#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import shelve
import subprocess

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

packages = sys.argv[1:]
# filter manifest files
packages = [v for v in packages if "Manifest" not in v]
gentoo_repo = '../gentoo/'


def command(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True,
                            universal_newlines=True)
    for line in proc.stdout:
        print(line.strip())
    return proc.returncode


conf_var = "shelve"
d = shelve.open(conf_var)
d["version"] = []
versions = []

# write script headers
with open('ebuild_merge.sh', 'w') as eb1:
    eb1.write("#!/bin/sh\n")
    eb1.write("set -e\n")

with open('ebuild_manifest.sh', 'w') as eb2:
    eb2.write("#!/bin/sh\n")
    eb2.write("set -e\n")


ebm = open("ebuild_manifest.sh", 'a')
ebg = open("ebuild_merge.sh", 'a')
for package in packages:
    # .sort(key=lambda s: [int(u) for u in s.split('.')]):
    print("Processing: {0}".format(package))
    ebuild_location = gentoo_repo + package
    ebuild_full = 'ROOT=kernel_sources/ /usr/bin/ebuild ' + ebuild_location
    print("  {0}".format(ebuild_full))

    ebm.write(ebuild_full + ' clean manifest\n')
    ebg.write(ebuild_full + ' merge\n')

    versions.append(package)
ebm.close()
ebg.close()

os.chmod('ebuild_merge.sh', 0o755)
os.chmod('ebuild_manifest.sh', 0o755)

result = command('./ebuild_manifest.sh')
if result > 0:
    print("Manifest generation failed")
    sys.exit(1)

result = command('./ebuild_merge.sh')
if result > 0:
    print("Emerging failed")
    sys.exit(1)

d["version"] = versions
d.close()
