import os

def nmap_scan(cmd):
    """unsafe method, should only be called by the admin"""
    hosts = []
    try:
        results = os.popen("%s | grep open" % cmd).read()
        for line in [line.rstrip().lower() for line in results.split("\n") if line]:
            if not line.startswith("host: "):
                continue
            spl = line.split(" ")
            host = spl[1]
            port = int(spl[3].split("/")[0])
            hosts.append([host, port])
    except Exception:
        pass
    return hosts
