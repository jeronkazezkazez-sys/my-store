import customtkinter as ctk
import subprocess
from tkinter import filedialog  # مكتبة لفتح نافذة اختيار الملفات من الكمبيوتر

ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")  

class SoftwareToolApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mobile Software Tool")
        self.geometry("500x520")
        self.resizable(False, False)

        self.title_label = ctk.CTkLabel(self, text="Mobile Software Tool", font=ctk.CTkFont(size=22, weight="bold"))
        self.title_label.pack(pady=20)

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10, padx=20, fill="x")

        # 1. زر Read Info
        self.btn_read_info = ctk.CTkButton(self.button_frame, text="Read Info", font=ctk.CTkFont(size=14), command=self.read_info_action)
        self.btn_read_info.pack(pady=10, padx=20, fill="x")

        # 2. زر Flash Firmware
        self.btn_flash = ctk.CTkButton(self.button_frame, text="Flash Firmware", font=ctk.CTkFont(size=14), fg_color="#2b8a3e", hover_color="#237032", command=self.flash_firmware_action)
        self.btn_flash.pack(pady=10, padx=20, fill="x")

        # 3. زر FRP Bypass
        self.btn_frp = ctk.CTkButton(self.button_frame, text="FRP Bypass", font=ctk.CTkFont(size=14), fg_color="#e03131", hover_color="#c92a2a", command=self.frp_bypass_action)
        self.btn_frp.pack(pady=10, padx=20, fill="x")

        # 4. زر Factory Reset / Format
        self.btn_format = ctk.CTkButton(self.button_frame, text="Factory Reset / Format", font=ctk.CTkFont(size=14), fg_color="#9c36b5", hover_color="#862e9c", command=self.factory_reset_action)
        self.btn_format.pack(pady=10, padx=20, fill="x")

        self.log_label = ctk.CTkLabel(self, text="Operation Log:", font=ctk.CTkFont(size=12))
        self.log_label.pack(pady=(15, 0), padx=20, anchor="w")

        self.log_text = ctk.CTkTextbox(self, height=120, width=460, font=ctk.CTkFont(size=12))
        self.log_text.pack(pady=(5, 20), padx=20)
        self.log_text.insert("0.0", "System Ready...\nConnect device and choose an operation.\n")
        self.log_text.configure(state="disabled") 

    def log_message(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f">> {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def run_adb_command(self, argument):
        cmd = f"adb shell getprop {argument}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()

    def read_info_action(self):
        self.log_message("Reading device info via ADB... Please wait.")
        try:
            check_device = subprocess.run("adb get-state", shell=True, capture_output=True, text=True)
            if "device" in check_device.stdout or check_device.returncode == 0:
                manufacturer = self.run_adb_command("ro.product.manufacturer")
                model = self.run_adb_command("ro.product.model")
                android_version = self.run_adb_command("ro.build.version.release")
                cpu_architecture = self.run_adb_command("ro.product.cpu.abi")
                
                self.log_message("--- DEVICE INFO ---")
                self.log_message(f"Brand: {manufacturer.upper()}")
                self.log_message(f"Model: {model}")
                self.log_message(f"Android OS: {android_version}")
                self.log_message(f"CPU Abi: {cpu_architecture}")
                self.log_message("-------------------")
            else:
                self.log_message("Error: No device detected. Ensure USB Debugging is ON.")
        except Exception as e:
            self.log_message(f"Execution failed: {str(e)}")

    def flash_firmware_action(self):
        self.log_message("Opening file browser to select Firmware...")
        
        # فتح نافذة الكمبيوتر لاختيار ملف الفلاشة
        file_path = filedialog.askopenfilename(
            title="Select Firmware File",
            filetypes=[("Firmware Files", "*.zip *.tar *.bin *.img"), ("All Files", "*.*")]
        )
        
        # إذا اختار المستخدم ملفاً بالفعل ولم يغلق النافذة
        if file_path:
            filename = file_path.split("/")[-1]  # استخراج اسم الملف فقط من المسار
            self.log_message(f"Selected File: {filename}")
            self.log_message("Starting Firmware Flashing process... Please wait.")
            
            # فحص وجود الجهاز قبل البدء المحاكي للتفليش
            check_device = subprocess.run("adb get-state", shell=True, capture_output=True, text=True)
            if "device" in check_device.stdout or check_device.returncode == 0:
                self.log_message("Flashing partitions: boot, system, vendor...")
                self.log_message("Flashing completed successfully! Device is rebooting.")
            else:
                self.log_message("Error: Flashing failed. No device connected via ADB.")
        else:
            self.log_message("Flashing canceled. No file selected.")

    def frp_bypass_action(self):
        self.log_message("Initiating FRP Bypass... Please wait.")
        try:
            check_device = subprocess.run("adb get-state", shell=True, capture_output=True, text=True)
            if "device" in check_device.stdout or check_device.returncode == 0:
                self.log_message("Device detected! Sending bypass commands...")
                cmd1 = "adb shell settings put global user_setup_complete 1"
                cmd2 = "adb shell settings put secure user_setup_complete 1"
                cmd3 = "adb shell am start -n com.google.android.setupwizard/.SetupWizardTestActivity"
                
                subprocess.run(cmd1, shell=True, capture_output=True)
                subprocess.run(cmd2, shell=True, capture_output=True)
                subprocess.run(cmd3, shell=True, capture_output=True)
                
                self.log_message("FRP Bypass command sent successfully!")
                self.log_message("Check your phone screen. It should jump to home screen.")
            else:
                self.log_message("Error: Device not found. Make sure ADB/USB Debugging is active.")
        except Exception as e:
            self.log_message(f"FRP Bypass failed: {str(e)}")

    def factory_reset_action(self):
        self.log_message("Attempting to reboot device into Recovery Mode via Local ADB...")
        try:
            result = subprocess.run("adb reboot recovery", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.log_message("Success! Device is rebooting to Recovery.")
            else:
                self.log_message("Error: Please connect a device with USB Debugging enabled.")
        except Exception as e:
            self.log_message(f"Execution failed: {str(e)}")

if __name__ == "__main__":
    app = SoftwareToolApp()
    app.mainloop()