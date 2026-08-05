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

# 2️⃣ رقم الواتساب الخاص بك
PHONE_NUMBER = "218916092788"

# 3️⃣ نموذج جدول المنتجات
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    is_available = db.Column(db.Boolean, default=True)

with app.app_context():
    db.create_all()

# 4️⃣ تصميم الواجهة المحدث
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
        
        /* المتجر العام */
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
        .card { background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.2s; position: relative; }
        .card:hover { transform: translateY(-5px); }
        .card img { width: 100%; height: 220px; object-fit: contain; background-color: #fff; cursor: zoom-in; padding: 5px; box-sizing: border-box; }
        .card-body { padding: 15px; }
        .card-title { font-size: 1.1em; font-weight: bold; margin-bottom: 10px; }
        .card-price { color: #e74c3c; font-size: 1.2em; font-weight: bold; margin-bottom: 15px; }
        
        .whatsapp-btn { display: block; text-align: center; background: #25D366; color: white; padding: 12px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 1em; }
        .whatsapp-btn:hover { background: #1eb854; }
        .out-of-stock-btn { display: block; text-align: center; background: #95a5a6; color: white; padding: 12px; border-radius: 5px; font-weight: bold; font-size: 1em; cursor: not-allowed; }
        .badge-out { position: absolute; top: 10px; right: 10px; background: #e74c3c; color: white; padding: 5px 10px; border-radius: 5px; font-size: 0.8em; font-weight: bold; }

        /* نافذة المعاينة */
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.85); justify-content: center; align-items: center; }
        .modal-content { max-width: 90%; max-height: 85%; border-radius: 8px; }
        .close-btn { position: absolute; top: 20px; right: 35px; color: #fff; font-size: 40px; font-weight: bold; cursor: pointer; }

        /* لوحة التحكم */
        .form-container { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
        .submit-btn { background: #27ae60; color: white; border: none; padding: 12px 20px; border-radius: 5px; cursor: pointer; width: 100%; font-size: 1em; font-weight: bold; }
        .cancel-btn { display: inline-block; background: #7f8c8d; color: white; text-decoration: none; padding: 10px 15px; border-radius: 5px; margin-top: 10px; }
        
        /* جدول إدارة المنتجات */
        table { width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        th, td { padding: 12px 15px; text-align: right; border-bottom: 1px solid #ddd; }
        th { background-color: #34495e; color: white; }
        .action-btn { padding: 6px 12px; border-radius: 4px; text-decoration: none; color: white; font-size: 0.9em; font-weight: bold; display: inline-block; }
        .edit-btn { background-color: #f39c12; }
        .delete-btn { background-color: #e74c3c; }
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
            <!-- نموذج إضافة أو تعديل منتج -->
            <div class="form-container">
                <h2>{% if edit_product %}تعديل بيانات المنتج{% else %}إضافة منتج جديد{% endif %}</h2>
                <form action="{% if edit_product %}/admin/edit/{{ edit_product.id }}{% else %}/admin{% endif %}" method="POST">
                    <div class="form-group">
                        <label>اسم المنتج أو الخدمة:</label>
                        <input type="text" name="name" value="{{ edit_product.name if edit_product else '' }}" placeholder="مثال: تفعيل أداة EFT Pro" required>
                    </div>
                    <div class="form-group">
                        <label>السعر (XOF):</label>
                        <input type="number" step="0.01" name="price" value="{{ edit_product.price if edit_product else '' }}" placeholder="مثال: 15000" required>
                    </div>
                    <div class="form-group">
                        <label>رابط صورة المنتج (Image URL):</label>
                        <input type="url" name="image_url" value="{{ edit_product.image_url if edit_product else '' }}" placeholder="https://example.com/image.jpg">
                    </div>
                    <div class="form-group">
                        <label>حالة التوفر في المخزن:</label>
                        <select name="is_available">
                            <option value="1" {% if edit_product and edit_product.is_available %}selected{% endif %}>متوفر في المخزن</option>
                            <option value="0" {% if edit_product and not edit_product.is_available %}selected{% endif %}>نفدت الكمية</option>
                        </select>
                    </div>
                    <button type="submit" class="submit-btn">{% if edit_product %}تحديث المنتج{% else %}حفظ المنتج{% endif %}</button>
                    {% if edit_product %}
                        <a href="/admin" class="cancel-btn">إلغاء التعديل</a>
                    {% endif %}
                </form>
            </div>

            <!-- جدول إدارة المنتجات -->
            <h2>قائمة المنتجات المضافة</h2>
            {% if products %}
                <table>
                    <thead>
                        <tr>
                            <th>الاسم</th>
                            <th>السعر</th>
                            <th>الحالة</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for p in products %}
                            <tr>
                                <td>{{ p.name }}</td>
                                <td>{{ "{:,.0f}".format(p.price) }} XOF</td>
                                <td>
                                    {% if p.is_available %}
                                        <span style="color: green; font-weight: bold;">متوفر</span>
                                    {% else %}
                                        <span style="color: red; font-weight: bold;">نفدت الكمية</span>
                                    {% endif %}
                                </td>
                                <td>
                                    <a href="/admin/edit/{{ p.id }}" class="action-btn edit-btn">تعديل</a>
                                    <a href="/admin/delete/{{ p.id }}" class="action-btn delete-btn" onclick="return confirm('هل أنت تأكد من حذف هذا المنتج؟');">حذف</a>
                                </td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p>لا توجد منتجات مضافة حتى الآن.</p>
            {% endif %}

        {% else %}
            <!-- الواجهة العامة للزبائن -->
            {% if products %}
                <div class="grid">
                    {% for p in products %}
                        <div class="card">
                            {% if not p.is_available %}
                                <div class="badge-out">غير متوفر</div>
                            {% endif %}
                            <img src="{{ p.image_url if p.image_url else 'https://via.placeholder.com/250x200?text=No+Image' }}" 
                                 alt="{{ p.name }}" 
                                 onclick="openModal(this.src)">
                            <div class="card-body">
                                <div class="card-title">{{ p.name }}</div>
                                <div class="card-price">{{ "{:,.0f}".format(p.price) }} XOF</div>
                                {% if p.is_available %}
                                    <a href="https://wa.me/{{ phone }}?text=أهلاً،%20أود%20شراء%20المنتج:%20{{ p.name }}" target="_blank" class="whatsapp-btn">💬 طلب عبر الواتساب</a>
                                {% else %}
                                    <div class="out-of-stock-btn">🚫 نفدت الكمية</div>
                                {% endif %}
                            </div>
                        </div>
                    {% endfor %}
                </div>
            {% else %}
                <p style="text-align: center;">لا توجد منتجات مضافة حالياً.</p>
            {% endif %}
        {% endif %}
    </div>

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

# 6️⃣ لوحة التحكم واضافة منتج
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        image_url = request.form.get('image_url')
        is_available = request.form.get('is_available') == '1'
        if name and price:
            new_prod = Product(name=name, price=float(price), image_url=image_url, is_available=is_available)
            db.session.add(new_prod)
            db.session.commit()
            return redirect(url_for('admin'))
    
    products = Product.query.all()
    return render_template_string(HTML_TEMPLATE, products=products, is_admin=True, edit_product=None, phone=PHONE_NUMBER)

# 7️⃣ تعديل منتج
@app.route('/admin/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.price = float(request.form.get('price'))
        product.image_url = request.form.get('image_url')
        product.is_available = request.form.get('is_available') == '1'
        db.session.commit()
        return redirect(url_for('admin'))
    
    products = Product.query.all()
    return render_template_string(HTML_TEMPLATE, products=products, is_admin=True, edit_product=product, phone=PHONE_NUMBER)

# 8️⃣ حذف منتج
@app.route('/admin/delete/<int:product_id>')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin'))

if __name__ == "__main__":
    app.run()
