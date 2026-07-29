from scapy.all import sniff, IP, TCP

def packet_callback(packet):
    # التأكد من أن الحزمة تحتوي على بروتوكول IP (إنترنت)
    if packet.haslayer(IP):
        ip_src = packet[IP].src   # آي بي المصدر (المرسل)
        ip_dst = packet[IP].dst   # آي بي الهدف (المستقبل)
        
        # إذا كانت الحزمة تستخدم بروتوكول TCP
        if packet.haslayer(TCP):
            port_src = packet[TCP].sport # منفذ المرسل
            port_dst = packet[TCP].dport # منفذ المستقبل
            
            print(f"[+] حزمة TCP: {ip_src}:{port_src} ---> {ip_dst}:{port_dst}")

print("جاري بدء مراقبة الشبكة... (اضغط Ctrl+C للإيقاف)")

# تشغيل المراقبة وفلترة حزم الـ IP فقط، واستدعاء الدالة لكل حزمة تمر
sniff(filter="ip", prn=packet_callback, count=20)