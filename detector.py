from scapy.all import sniff, IP, TCP

# الأي بي المحلي الخاص بجهازك (الذي ظهر في الفحص السابق)
MY_IP = "192.168.8.26"

# قائمة بالمنافذ الآمنة والطبيعية التي نستخدمها يومياً حتى لا يزعجنا السكربت بها
# 80 (HTTP), 443 (HTTPS), 53 (DNS)
SAFE_PORTS = [80, 443, 53]

def monitor_packet(packet):
    if packet.haslayer(IP) and packet.haslayer(TCP):
        ip_src = packet[IP].src
        ip_dst = packet[IP].dst
        port_src = packet[TCP].sport
        port_dst = packet[TCP].dport
        
        # 1. إذا كان جهازك هو الذي يرسل بيانات لخارج الشبكة عبر منفذ غير آمن
        if ip_src == MY_IP and port_dst not in SAFE_PORTS:
            print(f"\n[⚠️ تحذير - نشاط خارجي مشبوه]: برنامج في جهازك يتصل بسيرفر غريب!")
            print(f"الهدف: {ip_dst} عبر المنفذ: {port_dst}")
            print("-" * 50)
            
        # 2. إذا كان هناك آي بي خارجي يحاول الدخول لجهازك عبر منفذ غريب
        elif ip_dst == MY_IP and port_dst not in SAFE_PORTS:
            print(f"\n[🚨 إنذار - محاولة تدخل خارجي]: جهاز غريب يحاول الاتصال بك!")
            print(f"المصدر: {ip_src} يحاول الدخول عبر المنفذ: {port_dst}")
            print("-" * 50)

print("🛡️ نظام كشف التسلل الذكي يعمل الآن... يراقب جهازك في الخلفية...")
# تشغيل مستمر بدون تحديد count
sniff(filter="ip", prn=monitor_packet, store=0)