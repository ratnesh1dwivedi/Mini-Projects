import scapy.all as scapy

def scan(ip_range):
    # Create an ARP request packet
    arp_request = scapy.ARP(pdst=ip_range)
    
    # Create an Ethernet frame to encapsulate the ARP request
    ether = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    
    # Combine the Ethernet frame and ARP request packet
    packet = ether/arp_request
    
    # Send the packet and receive responses
    answered_list = scapy.srp(packet, timeout=1, verbose=False)[0]
    
    # Extract and return IP and MAC addresses of the devices
    devices_list = []
    for element in answered_list:
        device_info = {"ip": element[1].psrc, "mac": element[1].hwsrc}
        devices_list.append(device_info)
    return devices_list

if __name__ == "__main__":
    ip_range = "192.168.1.1/24"  # Change this to your local network's IP range
    devices = scan(ip_range)
    
    print("IP Address\t\tMAC Address")
    print("-----------------------------------------")
    for device in devices:
        print(device["ip"] + "\t\t" + device["mac"])
