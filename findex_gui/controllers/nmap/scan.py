import os

def nmap_scan(cmd):
    """unsafe method, should only be called by the admin. Yolo nmap parsing"""
    hosts = []
    try:
        results = os.popen("%s | grep open" % cmd).read()
        results = str(results)
        for line in [line.rstrip().lower() for line in results.split("\n") if line]:
            if not line.startswith("host: ") or "ports:" not in line:
                continue

            try:
                host = line[6:].split(" ", 1)[0]
                line = line[line.find("\t") + 8:]

                items = line.split("/, ")
                for item in items:
                    port, status, ip_protocol, not_sure, service, not_sure2, banner = item.split("/", 6)
                    if status != "open":
                        continue

                    port = int(port)
                    hosts.append({
                        "host": host,
                        "port": port,
                        "service": service})
            except:
                pass
    except Exception:
        pass
    return hosts
