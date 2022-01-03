# Parts of this file are:
# Copyright (c) 2007 Brandon Sterne
# 2015 Updates by Rafe Colburn
# Licensed under the MIT license.
# http://brandon.sternefamily.net/files/mit-license.txt
# CIDR Block Converter - 2007

def ip2bin(ip):
    b = ""
    inQuads = ip.split(".")
    outQuads = 4
    for q in inQuads:
        if q != "":
            b += dec2bin(int(q),8)
            outQuads -= 1
    while outQuads > 0:
        b += "00000000"
        outQuads -= 1
    return b

def dec2bin(n,d=None):
    s = ""
    while n>0:
        if n&1:
            s = "1"+s
        else:
            s = "0"+s
        n >>= 1
    if d is not None:
        while len(s)<d:
            s = "0"+s
    if s == "": s = "0"
    return s

def bin2ip(b):
    ip = ""
    for i in range(0,len(b),8):
        ip += str(int(b[i:i+8],2))+"."
    return ip[:-1]

def parse_cidr(str):
    splitted = str.split("/")

    if len(splitted) > 2:
        raise ValueError

    if len(splitted) == 1:
        subnet = 32
    else:
        subnet = int(splitted[1])

    if subnet > 32:
        raise ValueError

    str_ip = splitted[0]
    ip = str_ip.split(".")
    if len(ip) != 4:
        raise ValueError

    for i in ip:
        if int(i) < 0 or int(i) > 255:
            raise ValueError

    if subnet == 32:
        return [str_ip]

    bin_ip = ip2bin(str_ip)

    ip_prefix = bin_ip[:-(32-subnet)]

    ret = []
    for i in range(2**(32-subnet)):
        ret.append(bin2ip(ip_prefix+dec2bin(i, (32-subnet))))

    return ret

def get_ports(str):
    ports = []
    for x in str.split(","):
        x = x.strip()
        if "-" in x:
            x = x.split("-")
            if len(x) > 2:
                raise ValueError

            if int(x[0]) < 0 or int(x[0]) > 65535:
                raise ValueError
            if int(x[1]) < 0 or int(x[1]) + 1 > 65535:
                raise ValueError
            if int(x[0]) > int(x[1]) + 1:
                raise ValueError

            ports += range(int(x[0]), int(x[1]) + 1)
        else:
            if int(x) < 0 or int(x) > 65535:
                raise ValueError
            ports.append(int(x))

    return ports

def get_ips(str):
    ips = []
    for x in str.split(","):
        ips += parse_cidr(x.strip())
    return ips

if __name__ == "__main__":
    ips = get_ips("127.0.0.1,192.168.0.0/24,10.0.0.40/28")
    print(ips)
    ports = get_ports("4444,1-100,5432")
    print(ports)
