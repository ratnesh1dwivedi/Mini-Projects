import subprocess

def scan_ethernet_networks():
    try:
        # Run nmap command to scan all Ethernet networks
        result = subprocess.check_output(["nmap", "-sn", "192.168.0.0/16"], universal_newlines=True)
        return result
    except subprocess.CalledProcessError as e:
        return "Error: " + str(e)

if __name__ == "__main__":
    scan_result = scan_ethernet_networks()
    print(scan_result)
