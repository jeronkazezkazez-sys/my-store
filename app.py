from flask import Flask, render_template_string

app = Flask(__name__)

# الصفحة الرئيسية للمتجر
@app.route('/')
def home():
    html_content = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Smart Solutions Store | متجر الحلول الذكية</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; background-color: #f4f6f9; padding: 20px; }
            header { background: #1a252f; color: white; padding: 20px; border-radius: 10px; }
            .card { background: white; padding: 20px; margin: 15px auto; max-width: 400px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .btn { display: inline-block; padding: 10px 20px; color: white; background: #27ae60; text-decoration: none; border-radius: 5px; margin-top: 10px; }
        </style>
    </head>
    <body>
        <header>
            <h1>💡 Smart Solutions Store</h1>
            <p>متجر الحلول الذكية لصيانة الهواتف، السوفت وير، وقطع الغيار</p>
        </header>

        <div class="card">
            <h3>📱 خدمات السوفت وير والصيانة</h3>
            <p>فك شفرات، تخطي حسابات، وتحديث أنظمة الهواتف بأحدث الأدوات.</p>
        </div>

        <div class="card">
            <h3>🔋 قطع الغيار والإكسسوارات</h3>
            <p>توفير أفضل قطع الغيار والإكسسوارات الأصلية.</p>
        </div>

        <a href="https://wa.me/" class="btn">تواصل معنا عبر الواتساب 💬</a>
    </body>
    </html>
    """
    return render_template_string(html_content)

if __name__ == '_main_':
    app.run(host='0.0.0.0', port=5000)