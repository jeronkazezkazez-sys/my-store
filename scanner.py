from scapy.all import sniff, IP, TCP

MY_IP = "192.168.8.26"
SAFE_PORTS = [80, 443, 53]

def monitor_packet(packet):
    if packet.haslayer(IP) and packet.haslayer(TCP):
        ip_src = packet[IP].src
        ip_dst = packet[IP].dst
        port_src = packet[TCP].sport
        port_dst = packet[TCP].dport
        
        # 1. إذا كان جهازك يرسل بيانات غريبة للخارج
        if ip_src == MY_IP and port_dst not in SAFE_PORTS:
            print(f"\n[⚠️ WARNING - SUSPICIOUS OUTBOUND]: A program is connecting to an unknown server!")
            print(f"Target IP: {ip_dst} | Destination Port: {port_dst}")
            print("-" * 60)
            
        # 2. إذا كان هناك جهاز خارجي يحاول الدخول إليك
        elif ip_dst == MY_IP and port_dst not in SAFE_PORTS:
            print(f"\n[🚨 ALERT - INBOUND INTRUSION]: External device is trying to connect to you!")
            print(f"Source IP: {ip_src} | Target Port: {port_dst}")
            print("-" * 60)

print("🛡️ [IDS SYSTEM ACTIVE] - Monitoring your network traffic in the background...")
sniff(filter="ip", prn=monitor_packet, store=0)