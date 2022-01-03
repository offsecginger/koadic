#!/usr/bin/python3

import sys

syskey_data_file = sys.argv[1]

tmp_syskey = ""
syskey = ""
with open(syskey_data_file, 'rb') as syskeyfile:
    file_contents = syskeyfile.read()

i = 4220
while i < 28811:
    j = i + 15
    while i < j:
        tmp_syskey += file_contents[i:i+1].decode()
        i += 2
    i += 8176

tmp_syskey = list(map(''.join, zip(*[iter(tmp_syskey)]*2)))

transforms = [8, 5, 4, 2, 11, 9, 13, 3, 0, 6, 1, 12, 14, 10, 15, 7]
for i in transforms:
    syskey += tmp_syskey[i]

print("decoded SysKey: 0x%s" % syskey)
