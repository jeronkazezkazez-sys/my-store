import os
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# جلب رابط قاعدة البيانات ومعالجة البادئة
db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# رقم الواتساب الخاص بالمتجر (مع رمز الدولة بدون +)
PHONE_NUMBER = "218916092788"  # ضع رقمك هنا

# نموذج جدول المنتجات المعدل
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)  # رابط الصورة

with app.app_context():
    db.create_all()

# تصميم HTML حديث مع بطاقات ورابط الواتساب
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>متجر الحلول الذكية - Smart Solutions Store</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; color: #333; }
        .container { max-width: 900px; margin: auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #1a252f; margin-bottom: 5px; }
        .admin-link { display: inline-block; margin: 10px 0; padding: 8px 16px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; }
        
        /* تصميم كروت المنتجات */
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
        .card { background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; }
        .card img { width: 100%; height: 180px; object-fit: cover; background-color: #eee; }
        .card-body { padding: 15px; }
        .card-title { font-size: 1.1em; font-weight: bold; margin-bottom: 10px; }
        .card-price { color: #e74c3c; font-size: 1.2em; font-weight: bold; margin-bottom: 15px; }
        .whatsapp-btn { display: block; text-align: center; background: #25D366; color: white; padding: 10px; text-decoration: none; border-radius: 5px; font-weight: bold; }
        .whatsapp-btn:hover { background: #1eb854; }

        /* نموذج لوحة التحكم */
        .form-container { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        .submit-btn { background: #27ae60; color: white; border: none; padding: 12px 20px; border-radius: 5px; cursor: pointer; width: 100%; font-size: 1em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛠️ متجر الحلول الذكية</h1>
            <p>Smart Solutions Store</p>
            {% if not is_admin %}
                <a href="/admin" class="admin-link">⚙️ لوحة التحكم (إضافة منتج)</a>
            {% else %}
                <a href="/" class="admin-link">← العودة للمتجر</a>
            {% endif %}
        </div>

        {% if is_admin %}
            <div class="form-container">
                <h2>إضافة منتج جديد</h2>
                <form action="/admin" method="POST">
                    <div class="form-group">
                        <label>اسم المنتج أو الخدمة:</label>
                        <input type="text" name="name" placeholder="مثال: شاشة أيفون 11 أو تفعيل أداة" required>
                    </div>
                    <div class="form-group">
                        <label>السعر ($):</label>
                        <input type="number" step="0.01" name="price" placeholder="مثال: 50" required>
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
                            <img src="{{ p.image_url if p.image_url else 'https://via.placeholder.com/250x180?text=No+Image' }}" alt="{{ p.name }}">
                            <div class="card-body">
                                <div class="card-title">{{ p.name }}</div>
                                <div class="card-price">${{ p.price }}</div>
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
</body>
</html>
"""

@app.route('/')
def home():
    products = Product.query.all()
    return render_template_string(HTML_TEMPLATE, products=products, is_admin=False, phone=PHONE_NUMBER)

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
