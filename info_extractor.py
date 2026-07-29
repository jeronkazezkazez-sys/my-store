import requests
from bs4 import BeautifulSoup
import re
import time
import urllib3

# إيقاف تحذيرات الأمان المزعجة في الترمينال
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

target_url = "https://httpbin.org" 

print(f"[-] جاري الاتصال بالموقع وفحص النص بالكامل: {target_url}\n")
time.sleep(1)

try:
    # أضفنا verify=False هنا لحل مشكلة الاتصال في الويندوز
    response = requests.get(target_url, timeout=5, verify=False)
    page_text = response.text  
    
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\+?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{3,9}'
    
    extracted_emails = re.findall(email_pattern, page_text)
    extracted_phones = re.findall(phone_pattern, page_text)
    
    emails = list(set(extracted_emails))
    phones = list(set(extracted_phones))
    
    print("=" * 50)
    print(f"[🔎] نتائج الفحص والتحليل للموقع:")
    print("=" * 50)
    
    if emails:
        print(f"\n[📧] تم العثور على ({len(emails)}) إيميل:")
        for counter, email in enumerate(emails, 1):
            print(f"   [{counter}] -> {email}")
    else:
        print("\n[-] لم يتم العثور على أي إيميلات مكشوفة في هذه الصفحة.")
        
    if phones:
        valid_phones = [p for p in phones if len(re.sub(r'\D', '', p)) >= 7]
        if valid_phones:
            print(f"\n[📱] تم العثور على ({len(valid_phones)}) رقم هاتف محتمل:")
            for counter, phone in enumerate(valid_phones, 1):
                print(f"   [{counter}] -> {phone.strip()}")
        else:
            print("\n[-] لم يتم العثور على أرقام هواتف حقيقية.")
    else:
        print("\n[-] لم يتم العثور على أي أرقام هواتف في هذه الصفحة.")

# هنا قمنا بتعديل الكود ليطبع لك سبب الخطأ الحقيقي إذا فشل مجدداً
except requests.exceptions.RequestException as error:
    print(f"[!] فشل الاتصال. السبب الحقيقي: {error}")

print("\n" + "=" * 50)
print("[-] تم الانتهاء من فحص وجمع البيانات.")