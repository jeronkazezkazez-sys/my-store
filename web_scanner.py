import requests
import time

# 1. تحديد الموقع المستهدف لفحصه (سنستخدم موقعاً تجريبياً أو موقعاً معروفاً)
# تنبيه: افحص دائماً المواقع التي تملك إذنًا لفحصها
target_url = "https://www.google.com"  

# 2. قائمة المجلدات الشائعة التي نريد البحث عنها داخل الموقع
directories = [
    "admin", 
    "login", 
    "secret", 
    "images", 
    "test", 
    "backup", 
    "robots.txt", 
    "api"
]

print(f"[-] جاري بدء فحص المسارات المخفية للموقع: {target_url}\n")
time.sleep(1)

# 3. الحلقة التكرارية لفحص كل مسار
for directory in directories:
    # دمج رابط الموقع مع المسار (مثال: https://www.google.com/admin)
    full_url = f"{target_url}/{directory}"
    
    try:
        # إرسال طلب للموقع للتأكد من وجود الرابط
        response = requests.get(full_url, timeout=3)
        
        # رمز الحالة 200 يعني أن الصفحة موجودة وتعمل بنجاح!
        if response.status_code == 200:
            print(f"[🎉 وُجد المسار]: {full_url} ---> (الحالة: 200 OK)")
        # رمز الحالة 404 يعني أن الصفحة غير موجودة
        elif response.status_code == 404:
            print(f"[X غير موجود]: /{directory}")
        else:
            print(f"[!] استجابة أخرى /{directory} ---> (الحالة: {response.status_code})")
            
    except requests.exceptions.RequestException:
        print(f"[!] فشل الاتصال بالرابط: {full_url}")
        
    time.sleep(0.3) # فاصل زمني بسيط بين الطلبات

print("\n[-] تم الانتهاء من فحص الموقع بنجاح.")