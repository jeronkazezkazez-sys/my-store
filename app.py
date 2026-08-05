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

# جدول المنتجات
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

# HTML بسيط للواجهة
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>متجر الحلول الذكية - Smart Solutions Store</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; color: #333; }
        h1, h2 { color: #2c3e50; }
        .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        ul { list-style: none; padding: 0; }
        li { background: #eee; margin: 5px 0; padding: 10px; border-radius: 4px; display: flex; justify-content: space-between; }
        form { margin-top: 20px; display: flex; gap: 10px; }
        input[type="text"], input[type="number"] { padding: 8px; border: 1px solid #ccc; border-radius: 4px; flex: 1; }
        button { padding: 8px 15px; background: #27ae60; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #219150; }
        .admin-link { display: inline-block; margin-bottom: 15px; color: #2980b9; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛠️ متجر الحلول الذكية (Smart Solutions Store)</h1>
        {% if is_admin %}
            <h2>لوحة التحكم - إضافة منتج جديد</h2>
            <form action="/admin" method="POST">
                <input type="text" name="name" placeholder="اسم المنتج (مثال: شاشة أيفون 11)" required>
                <input type="number" step="0.01" name="price" placeholder="السعر" required>
                <button type="submit">إضافة المنتج</button>
            </form>
            <br>
            <a href="/" class="admin-link">← العودة للواجهة الرئيسية</a>
        {% else %}
            <a href="/admin" class="admin-link">⚙️ الانتقال إلى لوحة التحكم</a>
            <h2>قائمة المنتجات والخدمات المتاحة:</h2>
            {% if products %}
                <ul>
                    {% for p in products %}
                        <li><span>{{ p.name }}</span> <strong>${{ p.price }}</strong></li>
                    {% endfor %}
                </ul>
            {% else %}
                <p>لا توجد منتجات مضافة حتى الآن.</p>
            {% endif %}
        {% endif %}
    </div>
</body>
</html>
"""

# 1️⃣ الواجهة الرئيسية للمتجر
@app.route('/')
def home():
    products = Product.query.all()
    return render_template_string(HTML_TEMPLATE, products=products, is_admin=False)

# 2️⃣ لوحة التحكم لتأكيد وإضافة المنتجات
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        if name and price:
            new_prod = Product(name=name, price=float(price))
            db.session.add(new_prod)
            db.session.commit()
            return redirect(url_for('home'))
    
    return render_template_string(HTML_TEMPLATE, is_admin=True)

if __name__ == "__main__":
    app.run()
