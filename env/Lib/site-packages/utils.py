import re

class Device:
    def __init__(self, hostname=None, address=None):
        self.hostname=hostname
        self.address=address
    
    def __getstate__(self):
        return self.__dict__
    
    def __setstate__(self, state):
        self.__dict__=state


def extract_devices(response):
    if (len(response.text)==1):
        return None
    hostnames=re.findall("hostname=.+,", response.text)
    newhosts=[]
    for host in hostnames:
        h=re.findall("=.+,",host)[0]
        newhosts.append(h[1:len(h)-1])

    addresses=re.findall("address=.+]", response.text)
    newaddr=[]
    for addr in addresses:
        a=re.findall("=.+]",addr)[0]
        newaddr.append(a[1:len(a)-1])

    devices=[]
    for host, addr in zip(newhosts, newaddr):
        devices.append(Device(host, addr))
    
    return devices
