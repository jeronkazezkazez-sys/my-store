import requests
from bs4 import BeautifulSoup
import time

# 1. حدد الموقع الذي تريد استخراج الروابط منه
target_url = "https://www.google.com"

print(f"[-] جاري الاتصال بالموقع لجمع الروابط: {target_url}\n")
time.sleep(1)

try:
    # إرسال طلب للموقع لجلب كود الـ HTML
    response = requests.get(target_url, timeout=5)
    
    # تحضير وتحليل كود الصفحة باستخدام BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 2. البحث عن جميع وسم الروابط في الـ HTML وهو الوسم 'a' الذي يحتوي على 'href'
    links = soup.find_all('a')
    
    print(f"[🎉 نجاح]: تم العثور على {len(links)} رابط داخل الصفحة!\n")
    print("--- قائمة الروابط المستخرجة ---")
    
    # 3. حلقة تكرارية لطباعة الروابط المكتشفة
    counter = 1
    for link in links:
        href = link.get('href')
        
        # التأكد من أن الرابط ليس فارغاً
        if href:
            # إذا كان الرابط داخلياً (يبدأ بـ /) نقوم بدمجه مع رابط الموقع الرئيسي
            if href.startswith('/'):
                href = target_url + href
                
            print(f"[{counter}] -> {href}")
            counter += 1
            
except requests.exceptions.RequestException as e:
    print(f"[!] فشل الاتصال بالموقع. تأكد من الرابط أو اتصال الإنترنت لديك.")

print("\n[-] تم الانتهاء من جمع المعلومات.")
