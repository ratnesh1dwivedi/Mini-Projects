import socket
from datetime import datetime

def is_valid_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def scan_ports(ip, start_port, end_port):
    print(f"\nScanning {ip} from port {start_port} to {end_port}...\n")
    open_ports = []
    for port in range(start_port, end_port + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except Exception as e:
            print(f"Error scanning port {port}: {e}")
    return open_ports

def main():
    ip = input("Enter IP address to scan: ").strip()
    if not is_valid_ip(ip):
        print("Invalid IP address.")
        return

    try:
        start_port = int(input("Enter start port (0-65535): "))
        end_port = int(input("Enter end port (0-65535): "))
        if not (0 <= start_port <= 65535 and 0 <= end_port <= 65535 and start_port <= end_port):
            raise ValueError
    except ValueError:
        print("Invalid port range.")
        return

    start_time = datetime.now()
    open_ports = scan_ports(ip, start_port, end_port)
    end_time = datetime.now()

    print("\nScan completed.")
    if open_ports:
        print("Open ports:")
        for port in open_ports:
            print(f"Port {port} is open")
    else:
        print("No open ports found.")

    print(f"Time taken: {end_time - start_time}")

if __name__ == "__main__":
    main()
