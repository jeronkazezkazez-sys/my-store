from cryptography.fernet import Fernet
import arabic_reshaper
from bidi.algorithm import get_display

# دالة لقراءة النص العربي إذا كان مقلوباً في جهازك
def print_arabic(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    print(bidi_text)

# 1. توليد "مفتاح التشفير" (Key) - هذا هو المفتاح السري الذي يقفل ويفتح البيانات
# في العمل الحقيقي، يجب حفظ هذا المفتاح في مكان آمن جداً
secret_key = Fernet.generate_key()
cipher_suite = Fernet(secret_key)

print_arabic("[+] تم توليد مفتاح التشفير السري بنجاح.")
print(f"المفتاح السري (Key): {secret_key.decode()}\n")
print("-" * 50)

# 2. النص المراد تشفيره (مثلاً: كلمة مرور أو بيانات حساسة)
original_text = "MySecretPassword123"
print_arabic(f"[+] النص الأصلي قبل التشفير:")
print(f"{original_text}\n")

# 3. عملية التشفير (Encryption)
# نقوم بتحويل النص إلى بايتس (bytes) ثم تشفيره
encrypted_text = cipher_suite.encrypt(original_text.encode())
print_arabic("[🔒] النص بعد التشفير (أصبح رموزاً عشوائية لا يمكن قراءتها):")
print(f"{encrypted_text.decode()}\n")
print("-" * 50)

# 4. عملية فك التشفير (Decryption)
# باستخدام نفس المفتاح السري، نعيد النص لشغله الأصلي
decrypted_text = cipher_suite.decrypt(encrypted_text).decode()
print_arabic("[🔓] النص بعد فك التشفير (باستخدام المفتاح الصحيح):")
print(f"{decrypted_text}")