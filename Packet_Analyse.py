import scapy.all as scapy
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(filename='packet_sniffer.log', level=logging.INFO, format='%(asctime)s - %(message)s')

packet_count = 0

def packet_sniffer(packet):
    global packet_count
    packet_count += 1

    if packet.haslayer(scapy.IP):
        source_ip = packet[scapy.IP].src
        destination_ip = packet[scapy.IP].dst
        protocol = packet[scapy.IP].proto

        log_message = f"Packet #{packet_count} - Source IP: {source_ip}, Destination IP: {destination_ip}, Protocol: {protocol}"
        print(log_message)
        logging.info(log_message)

        if packet.haslayer(scapy.Raw):
            payload = packet[scapy.Raw].load
            log_message = f"Packet #{packet_count} - Payload: {payload}"
            print(log_message)
            logging.info(log_message)

def main(interface, filter_ip=None, filter_protocol=None):
    def custom_filter(packet):
        if filter_ip and packet.haslayer(scapy.IP):
            if packet[scapy.IP].src != filter_ip and packet[scapy.IP].dst != filter_ip:
                return False
        if filter_protocol and packet.haslayer(scapy.IP):
            if packet[scapy.IP].proto != filter_protocol:
                return False
        return True

    print(f"Starting packet sniffing on {interface}...")
    if filter_ip:
        print(f"Filtering packets with IP: {filter_ip}")
    if filter_protocol:
        print(f"Filtering packets with Protocol: {filter_protocol}")
    
    scapy.sniff(iface=interface, prn=packet_sniffer, store=False, lfilter=custom_filter)

if __name__ == "__main__":
    try:
        interface = input("Enter the interface to sniff (e.g., eth0): ")
        filter_ip = input("Enter the IP address to filter (press Enter to skip): ") or None
        filter_protocol = input("Enter the Protocol number to filter (press Enter to skip): ") or None
        filter_protocol = int(filter_protocol) if filter_protocol else None
        
        main(interface, filter_ip, filter_protocol)
    except ValueError:
        print("Invalid protocol number. Please enter a valid integer.")
    except Exception as e:
        print(f"An error occurred: {e}")
