import socket

def scan_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        if result == 0:
            print(f"Port {port} is open")
        else:
            print(f"Port {port} is closed")
        sock.close()
    except KeyboardInterrupt:
        print("Scan interrupted by user")
        exit()
    except socket.gaierror:
        print("Hostname could not be resolved")
        exit()
    except socket.error:
        print("Couldn't connect to server")
        exit()

if __name__ == "__main__":
    target_host = input("Enter target host IP: ")
    try:
        target_ip = socket.gethostbyname(target_host)
        print(f"Scanning target: {target_host} ({target_ip})")
    except socket.gaierror:
        print("Hostname could not be resolved")
        exit()

    for port in range(1, 1025):
        scan_port(target_host, port)
