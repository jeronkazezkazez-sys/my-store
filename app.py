import os
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 1️⃣ جلب رابط قاعدة البيانات ومعالجة البادئة
db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# 2️⃣ رقم الواتساب الخاص بك (ضع رقمك مع رمز الدولة بدون +)
PHONE_NUMBER = "218916092788"

# 3️⃣ نموذج جدول المنتجات
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)

with app.app_context():
    db.create_all()

# 4️⃣ تصميم الواجهة مع نافذة تكبير الصورة (Lightbox)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛠️ متجر الحلول الذكية 🛍️</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; color: #333; }
        .container { max-width: 900px; margin: auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #1a252f; margin-bottom: 5px; font-size: 1.8em; }
        .back-link { display: inline-block; margin: 10px 0; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; }
        
        /* تصميم بطاقات المنتجات */
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
        .card { background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.2s; }
        .card:hover { transform: translateY(-5px); }
        .card img { width: 100%; height: 220px; object-fit: contain; background-color: #fff; cursor: zoom-in; padding: 5px; box-sizing: border-box; }
        .card-body { padding: 15px; }
        .card-title { font-size: 1.1em; font-weight: bold; margin-bottom: 10px; }
        .card-price { color: #e74c3c; font-size: 1.2em; font-weight: bold; margin-bottom: 15px; }
        .whatsapp-btn { display: block; text-align: center; background: #25D366; color: white; padding: 12px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 1em; }
        .whatsapp-btn:hover { background: #1eb854; }

        /* نافذة العرض المكبر للصورة */
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.85); justify-content: center; align-items: center; }
        .modal-content { max-width: 90%; max-height: 85%; border-radius: 8px; box-shadow: 0 0 20px rgba(255,255,255,0.2); }
        .close-btn { position: absolute; top: 20px; right: 35px; color: #fff; font-size: 40px; font-weight: bold; cursor: pointer; }

        /* نموذج لوحة التحكم */
        .form-container { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        .submit-btn { background: #27ae60; color: white; border: none; padding: 12px 20px; border-radius: 5px; cursor: pointer; width: 100%; font-size: 1em; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛠️ متجر الحلول الذكية 🛍️</h1>
            <p>Smart Solutions Store</p>
            {% if is_admin %}
                <a href="/" class="back-link">← العودة للمتجر العام</a>
            {% endif %}
        </div>

        {% if is_admin %}
            <div class="form-container">
                <h2>لوحة التحكم - إضافة منتج جديد</h2>
                <form action="/admin" method="POST">
                    <div class="form-group">
                        <label>اسم المنتج أو الخدمة:</label>
                        <input type="text" name="name" placeholder="مثال: شاشة أيفون 11 أو تفعيل أداة" required>
                    </div>
                    <div class="form-group">
                        <label>السعر بالعملة الأفريقية (XOF):</label>
                        <input type="number" step="0.01" name="price" placeholder="مثال: 15000" required>
                    </div>
                    <div class="form-group">
                        <label>رابط صورة المنتج (Image URL):</label>
                        <input type="url" name="image_url" placeholder="https://example.com/image.jpg">
                    </div>
                    <button type="submit" class="submit-btn">حفظ المنتج</button>
                </form>
            </div>
        {% else %}
            {% if products %}
                <div class="grid">
                    {% for p in products %}
                        <div class="card">
                            <img src="{{ p.image_url if p.image_url else 'https://via.placeholder.com/250x200?text=No+Image' }}" 
                                 alt="{{ p.name }}" 
                                 title="اضغط لتكبير الصورة"
                                 onclick="openModal(this.src)">
                            <div class="card-body">
                                <div class="card-title">{{ p.name }}</div>
                                <div class="card-price">{{ "{:,.0f}".format(p.price) }} XOF</div>
                                <a href="https://wa.me/{{ phone }}?text=أهلاً،%20أود%20شراء%20المنتج:%20{{ p.name }}" target="_blank" class="whatsapp-btn">💬 طلب عبر الواتساب</a>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            {% else %}
                <p style="text-align: center;">لا توجد منتجات مضافة حالياً.</p>
            {% endif %}
        {% endif %}
    </div>

    <!-- النافذة المكبرة للصورة -->
    <div id="imageModal" class="modal" onclick="closeModal()">
        <span class="close-btn">&times;</span>
        <img class="modal-content" id="fullImage">
    </div>

    <script>
        function openModal(src) {
            document.getElementById("fullImage").src = src;
            document.getElementById("imageModal").style.display = "flex";
        }
        function closeModal() {
            document.getElementById("imageModal").style.display = "none";
        }
    </script>
</body>
</html>
"""

# 5️⃣ الرابط العام للمتجر
@app.route('/')
def home():
    products = Product.query.all()
    return render_template_string(HTML_TEMPLATE, products=products, is_admin=False, phone=PHONE_NUMBER)

# 6️⃣ رابط لوحة التحكم
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        image_url = request.form.get('image_url')
        if name and price:
            new_prod = Product(name=name, price=float(price), image_url=image_url)
            db.session.add(new_prod)
            db.session.commit()
            return redirect(url_for('home'))
    
    return render_template_string(HTML_TEMPLATE, is_admin=True, phone=PHONE_NUMBER)

if __name__ == "__main__":
    app.run()
