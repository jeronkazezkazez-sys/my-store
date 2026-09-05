import os
import csv
import io
from flask import Flask, render_template_string, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, func

app = Flask(__name__)

# 1️⃣ جلب رابط قاعدة البيانات ومعالجة البادئة
db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# 2️⃣ رقم الواتساب والعملة
PHONE_NUMBER = "218916092788"
CURRENCY = "CFA"

# 3️⃣ نماذج جداول قاعدة البيانات
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float, nullable=True)
    category = db.Column(db.String(50), default="تفعيلات وبوكسات")
    image_url = db.Column(db.String(500), nullable=True)
    is_available = db.Column(db.Boolean, default=True)

class VisitorLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(150), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

# 4️⃣ تحديث الهيكل وإنشاء الأعمدة والجدول الجديد تلقائياً
with app.app_context():
    db.create_all()
    try:
        db.session.execute(text("ALTER TABLE product ADD COLUMN IF NOT EXISTS is_available BOOLEAN DEFAULT TRUE;"))
        db.session.execute(text("ALTER TABLE product ADD COLUMN IF NOT EXISTS old_price FLOAT;"))
        db.session.execute(text("ALTER TABLE product ADD COLUMN IF NOT EXISTS category VARCHAR(50) DEFAULT 'تفعيلات وبوكسات';"))
        db.session.commit()
    except Exception as e:
        db.session.rollback()

# 5️⃣ تصميم الواجهة المطور والمتناسق
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛠️ متجر الحلول الذكية | Smart Solutions Store 🛍️</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; font-family: 'Tajawal', sans-serif; }
        body { margin: 0; padding: 0; background-color: #f4f6f9; color: #2c3e50; padding-bottom: 80px; top: 0 !important; }
        
        .top-navbar { background: #1e3c72; color: white; padding: 10px 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
        .announcement { font-size: 0.9em; font-weight: 500; }
        
        .lang-switcher { display: flex; gap: 8px; align-items: center; }
        .lang-btn { background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.3); color: white; padding: 5px 12px; border-radius: 20px; font-size: 0.85em; font-weight: bold; cursor: pointer; transition: 0.3s; display: flex; align-items: center; gap: 5px; }
        .lang-btn:hover, .lang-btn.active { background: #25D366; border-color: #25D366; }

        .container { max-width: 1100px; margin: auto; padding: 20px 15px; }
        .header { text-align: center; margin-bottom: 25px; }
        .header h1 { color: #1a252f; margin: 10px 0 5px 0; font-size: 2em; font-weight: 800; }
        .header p { color: #7f8c8d; margin: 0; font-size: 1em; }
        .back-link { display: inline-block; margin-top: 15px; padding: 8px 18px; background: #34495e; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 0.9em; }

        /* ترتيب لوحة التحكم بجانب بعض لمظهر أكثر تناسقاً */
        .admin-dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; margin-bottom: 25px; }
        
        .category-filter { display: flex; justify-content: center; gap: 10px; margin-bottom: 25px; flex-wrap: wrap; }
        .filter-btn { padding: 8px 18px; border: 1px solid #dcdde1; border-radius: 20px; background: white; color: #2c3e50; font-weight: bold; cursor: pointer; transition: 0.3s; }
        .filter-btn.active, .filter-btn:hover { background: #25D366; color: white; border-color: #25D366; }

        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; }
        .card { background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; transition: all 0.3s ease; position: relative; border: 1px solid #edf2f7; }
        .card:hover { transform: translateY(-4px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }
        .card-img-wrapper { position: relative; background: #fff; width: 100%; height: 210px; display: flex; align-items: center; justify-content: center; padding: 10px; border-bottom: 1px solid #f1f2f6; }
        .card img { max-width: 100%; max-height: 100%; object-fit: contain; cursor: zoom-in; }
        
        .badge-out { position: absolute; top: 10px; right: 10px; background: #e74c3c; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.75em; font-weight: bold; }
        .badge-sale { position: absolute; top: 10px; left: 10px; background: #e67e22; color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.75em; font-weight: bold; }
        
        .card-body { padding: 15px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }
        .card-category { font-size: 0.75em; color: #95a5a6; font-weight: bold; text-transform: uppercase; margin-bottom: 4px; }
        .card-title { font-size: 1.05em; font-weight: 700; margin-bottom: 10px; line-height: 1.3; color: #2c3e50; }
        
        .price-container { margin-bottom: 15px; display: flex; align-items: baseline; gap: 8px; }
        .card-price { color: #e74c3c; font-size: 1.25em; font-weight: 800; }
        .card-old-price { color: #95a5a6; font-size: 0.95em; text-decoration: line-through; }

        .add-cart-btn { display: block; width: 100%; border: none; text-align: center; background: #1e3c72; color: white; padding: 10px; border-radius: 8px; font-weight: bold; font-size: 0.95em; cursor: pointer; transition: 0.2s; }
        .add-cart-btn:hover { background: #2a5298; }
        .out-of-stock-btn { display: block; text-align: center; background: #bdc3c7; color: white; padding: 10px; border-radius: 8px; font-weight: bold; font-size: 0.95em; cursor: not-allowed; }

        .cart-floating-btn { position: fixed; bottom: 20px; left: 20px; background: #25D366; color: white; border: none; border-radius: 30px; padding: 12px 22px; font-size: 1.05em; font-weight: bold; box-shadow: 0 4px 20px rgba(0,0,0,0.25); cursor: pointer; display: flex; align-items: center; gap: 10px; z-index: 99; transition: transform 0.2s; }
        .cart-floating-btn:hover { transform: scale(1.05); }
        .cart-badge { background: #e74c3c; color: white; border-radius: 50%; padding: 2px 8px; font-size: 0.85em; }

        .cart-modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.6); justify-content: center; align-items: center; }
        .cart-content { background: white; width: 90%; max-width: 500px; border-radius: 12px; padding: 20px; max-height: 80vh; display: flex; flex-direction: column; box-shadow: 0 5px 25px rgba(0,0,0,0.2); }
        .cart-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        .cart-header h3 { margin: 0; font-size: 1.3em; }
        .close-cart { cursor: pointer; font-size: 1.5em; font-weight: bold; color: #7f8c8d; }
        .cart-items { flex-grow: 1; overflow-y: auto; margin: 15px 0; }
        .cart-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f9f9f9; }
        .cart-item-info { font-size: 0.95em; }
        .cart-item-title { font-weight: bold; }
        .cart-item-price { color: #e74c3c; font-size: 0.85em; }
        .remove-item { color: #e74c3c; cursor: pointer; font-weight: bold; margin-right: 10px; }
        .cart-total { font-size: 1.2em; font-weight: bold; text-align: left; margin-top: 10px; border-top: 2px solid #eee; padding-top: 10px; }
        .send-whatsapp-btn { background: #25D366; color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 1em; cursor: pointer; text-align: center; text-decoration: none; display: block; margin-top: 15px; }

        .trust-features { display: flex; justify-content: space-around; background: white; margin-top: 40px; padding: 20px 10px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); flex-wrap: wrap; gap: 15px; text-align: center; }
        .feature-item { flex: 1; min-width: 150px; }
        .feature-icon { font-size: 1.8em; margin-bottom: 5px; }
        .feature-title { font-weight: bold; font-size: 0.95em; color: #2c3e50; }
        .feature-desc { font-size: 0.8em; color: #7f8c8d; }

        .goog-te-banner-frame { display: none !important; }
        #google_translate_element { display: none !important; }

        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.85); justify-content: center; align-items: center; }
        .modal-content { max-width: 90%; max-height: 85%; border-radius: 8px; }

        .form-container, .stats-container, .bulk-container { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); height: 100%; }
        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; font-size: 0.85em; }
        .form-group input, .form-group select { width: 100%; padding: 8px 10px; border: 1px solid #dcdde1; border-radius: 6px; box-sizing: border-box; font-size: 0.9em; }
        .submit-btn { background: #27ae60; color: white; border: none; padding: 10px 15px; border-radius: 6px; cursor: pointer; width: 100%; font-size: 0.95em; font-weight: bold; }
        .bulk-btn { background: #2980b9; color: white; border: none; padding: 10px 15px; border-radius: 6px; cursor: pointer; font-size: 0.9em; font-weight: bold; }
        .cancel-btn { display: inline-block; background: #7f8c8d; color: white; text-decoration: none; padding: 8px 12px; border-radius: 6px; margin-top: 10px; text-align: center; font-weight: bold; font-size: 0.85em; }
        
        table { width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-top: 15px; }
        th, td { padding: 10px 12px; text-align: right; border-bottom: 1px solid #f1f2f6; font-size: 0.85em; }
        th { background-color: #2c3e50; color: white; font-weight: bold; }
        .action-btn { padding: 4px 8px; border-radius: 4px; text-decoration: none; color: white; font-size: 0.8em; font-weight: bold; display: inline-block; }
        .edit-btn { background-color: #f39c12; }
        .delete-btn { background-color: #e74c3c; }
        .clear-logs-btn { background-color: #c0392b; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-size: 0.8em; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; }

        .alert-success { background: #d4edda; color: #155724; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-weight: bold; font-size: 0.9em; }
        .alert-danger { background: #f8d7da; color: #721c24; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-weight: bold; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="top-navbar">
        <div class="announcement">⚡ مرحباً بكم في متجر الحلول الذكية | Smart Solutions Store ⚡</div>
        
        <div class="lang-switcher">
            <button class="lang-btn active" onclick="changeLanguage('ar', this)">🇸🇦 العربية</button>
            <button class="lang-btn" onclick="changeLanguage('fr', this)">🇫🇷 Français</button>
            <button class="lang-btn" onclick="changeLanguage('en', this)">🇬🇧 English</button>
        </div>
    </div>

    <div id="google_translate_element"></div>

    <div class="container">
        <div class="header">
            <h1>🛠️ متجر الحلول الذكية 🛍️</h1>
            <p>Smart Solutions Store</p>
            {% if is_admin %}
                <a href="/" class="back-link">← العودة للمتجر العام</a>
            {% endif %}
        </div>

        {% if is_admin %}
            {% if msg %}
                <div class="alert-success">{{ msg }}</div>
            {% endif %}
            {% if err %}
                <div class="alert-danger">{{ err }}</div>
            {% endif %}

            <!-- شبكة تحكم متناسقة ومختصرة للطول -->
            <div class="admin-dashboard-grid">
                <!-- قسم رفع CSV -->
                <div class="bulk-container">
                    <h3 style="margin-top:0;">📁 رفع منتجات (CSV)</h3>
                    <p style="color: #7f8c8d; font-size: 0.8em; margin-bottom: 10px;">
                        اختر ملف CSV بالأعمدة: <code>name, price, old_price, category, image_url, is_available</code>
                    </p>
                    <form action="/admin/upload-csv" method="POST" enctype="multipart/form-data" style="display: flex; flex-direction: column; gap: 10px;">
                        <input type="file" name="csv_file" accept=".csv" required style="padding: 6px; background: #f8f9fa; border: 1px solid #ccc; border-radius: 6px; font-size: 0.85em;">
                        <button type="submit" class="bulk-btn">🚀 رفع واستيراد الملف</button>
                    </form>
                </div>

                <!-- لوحة إحصائيات الأجهزة مع زر مسح السجلات -->
                <div class="stats-container">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <h3 style="margin: 0;">📊 أجهزة الزوار</h3>
                        {% if device_stats %}
                            <a href="/admin/clear-logs" class="clear-logs-btn" onclick="return confirm('هل أنت تأكد من مسح جميع سجلات أجهزة الزوار؟');">🗑️ مسح السجلات</a>
                        {% endif %}
                    </div>
                    {% if device_stats %}
                        <table>
                            <thead>
                                <tr>
                                    <th>الجهاز</th>
                                    <th>الزيارات</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for stat in device_stats %}
                                    <tr>
                                        <td><b>📱 {{ stat.device_name }}</b></td>
                                        <td><span style="background: #e1f5fe; color: #0288d1; padding: 2px 8px; border-radius: 10px; font-weight: bold;">{{ stat.count }}</span></td>
                                    </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    {% else %}
                        <p style="color: #7f8c8d; font-size: 0.85em;">لا توجد سجلات حالياً.</p>
                    {% endif %}
                </div>
            </div>

            <div class="form-container" style="margin-bottom: 25px;">
                <h2>{% if edit_product %}تعديل بيانات المنتج{% else %}إضافة منتج يدوي فردي{% endif %}</h2>
                <form action="{% if edit_product %}/admin/edit/{{ edit_product.id }}{% else %}/admin{% endif %}" method="POST">
                    <div class="form-group">
                        <label>اسم المنتج أو الخدمة:</label>
                        <input type="text" name="name" value="{{ edit_product.name if edit_product else '' }}" placeholder="مثال: تفعيل أداة EFT Pro" required>
                    </div>
                    <div class="form-group">
                        <label>القسم:</label>
                        <select name="category">
                            <option value="تفعيلات وبوكسات" {% if edit_product and edit_product.category == 'تفعيلات وبوكسات' %}selected{% endif %}>تفعيلات وبوكسات</option>
                            <option value="قطع غيار وإكسسوارات" {% if edit_product and edit_product.category == 'قطع غيار وإكسسوارات' %}selected{% endif %}>قطع غيار وإكسسوارات</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>السعر الحقيقي (CFA):</label>
                        <input type="number" step="0.01" name="price" value="{{ edit_product.price if edit_product else '' }}" placeholder="مثال: 12000" required>
                    </div>
                    <div class="form-group">
                        <label>السعر قبل الخصم (اختياري):</label>
                        <input type="number" step="0.01" name="old_price" value="{{ edit_product.old_price if edit_product and edit_product.old_price else '' }}" placeholder="مثال: 15000">
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

            <h2>قائمة المنتجات المضافة</h2>
            {% if products %}
                <table>
                    <thead>
                        <tr>
                            <th>الاسم</th>
                            <th>القسم</th>
                            <th>السعر الحالي</th>
                            <th>السعر السابق</th>
                            <th>الحالة</th>
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for p in products %}
                            <tr>
                                <td><b>{{ p.name }}</b></td>
                                <td>{{ p.category }}</td>
                                <td>{{ "{:,.0f}".format(p.price) }} CFA</td>
                                <td>{{ "{:,.0f}".format(p.old_price) if p.old_price else '-' }}</td>
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
            <div class="category-filter">
                <button class="filter-btn active" onclick="filterCategory('all', this)">📌 الكل</button>
                <button class="filter-btn" onclick="filterCategory('تفعيلات وبوكسات', this)">💻 تفعيلات وبوكسات</button>
                <button class="filter-btn" onclick="filterCategory('قطع غيار وإكسسوارات', this)">🔌 قطع غيار وإكسسوارات</button>
            </div>

            {% if products %}
                <div class="grid">
                    {% for p in products %}
                        <div class="card product-card" data-category="{{ p.category }}">
                            {% if not p.is_available %}
                                <div class="badge-out">غير متوفر</div>
                            {% elif p.old_price and p.old_price > p.price %}
                                <div class="badge-sale">عرض خاص 🔥</div>
                            {% endif %}
                            
                            <div class="card-img-wrapper">
                                <img src="{{ p.image_url if p.image_url else 'https://via.placeholder.com/250x200?text=No+Image' }}" 
                                     alt="{{ p.name }}" 
                                     onclick="openModal(this.src)">
                            </div>

                            <div class="card-body">
                                <div>
                                    <div class="card-category">{{ p.category }}</div>
                                    <div class="card-title">{{ p.name }}</div>
                                </div>
                                <div>
                                    <div class="price-container">
                                        <span class="card-price">{{ "{:,.0f}".format(p.price) }} CFA</span>
                                        {% if p.old_price and p.old_price > p.price %}
                                            <span class="card-old-price">{{ "{:,.0f}".format(p.old_price) }} CFA</span>
                                        {% endif %}
                                    </div>
                                    {% if p.is_available %}
                                        <button class="add-cart-btn" onclick="addToCart('{{ p.name }}', {{ p.price }})">🛒 أضف إلى السلة</button>
                                    {% else %}
                                        <div class="out-of-stock-btn">🚫 نفدت الكمية</div>
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            {% else %}
                <p style="text-align: center; color: #7f8c8d;">لا توجد منتجات مضافة حالياً.</p>
            {% endif %}

            <button class="cart-floating-btn" onclick="openCartModal()">
                🛒 السلة
                <span class="cart-badge" id="cartCount">0</span>
            </button>

            <div id="cartModal" class="cart-modal">
                <div class="cart-content">
                    <div class="cart-header">
                        <h3>🛍️ سلة المشتريات</h3>
                        <span class="close-cart" onclick="closeCartModal()">&times;</span>
                    </div>
                    <div class="cart-items" id="cartItemsContainer">
                        <p style="text-align:center; color:#7f8c8d;">السلة فارغة حالياً.</p>
                    </div>
                    <div class="cart-total">
                        الإجمالي: <span id="cartTotalSum" style="color:#e74c3c;">0</span> CFA
                    </div>
                    <a id="whatsappOrderBtn" href="#" target="_blank" class="send-whatsapp-btn">💬 إرسال الطلب عبر الواتساب</a>
                </div>
            </div>

            <div class="trust-features">
                <div class="feature-item">
                    <div class="feature-icon">⚡</div>
                    <div class="feature-title">تسليم سريع</div>
                    <div class="feature-desc">تفعيل فوري ودقيق للمفاتيح والخدمات</div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">✔️</div>
                    <div class="feature-title">منتجات أصيلة</div>
                    <div class="feature-desc">قطع غيار ومعدات مفحوصة ومضمونة</div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">🛠️</div>
                    <div class="feature-title">دعم وتوجيه</div>
                    <div class="feature-desc">استشارات تقنية متواصلة عبر الواتساب</div>
                </div>
            </div>
        {% endif %}
    </div>

    <div id="imageModal" class="modal" onclick="closeModal()">
        <span class="close-btn" style="position:absolute; top:20px; right:35px; color:#fff; font-size:40px; cursor:pointer;">&times;</span>
        <img class="modal-content" id="fullImage">
    </div>

    <script type="text/javascript">
        function googleTranslateElementInit() {
            new google.translate.TranslateElement({
                pageLanguage: 'ar',
                includedLanguages: 'ar,fr,en',
                layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
                autoDisplay: false
            }, 'google_translate_element');
        }
    </script>
    <script type="text/javascript" src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>

    <script>
        let cart = [];
        const phoneNumber = "{{ phone }}";

        function detectUserDevice() {
            const ua = navigator.userAgent;
            if (/Android/i.test(ua)) {
                let match = ua.match(/Android[^;]+; ([^;]+)\)/);
                return match ? match[1] : "Android Device";
            } else if (/iPhone/i.test(ua)) {
                return "iPhone";
            } else if (/iPad/i.test(ua)) {
                return "iPad";
            } else if (/Windows/i.test(ua)) {
                return "Windows PC";
            } else if (/Mac/i.test(ua)) {
                return "Mac PC";
            }
            return "Other Device";
        }

        window.addEventListener('DOMContentLoaded', () => {
            const device = detectUserDevice();
            fetch('/api/log-visitor-device', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ device_name: device })
            }).catch(e => console.log('Analytics logged.'));
        });

        function changeLanguage(langCode, btn) {
            let btns = document.querySelectorAll('.lang-btn');
            btns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            let select = document.querySelector('.goog-te-combo');
            if (select) {
                select.value = langCode;
                select.dispatchEvent(new Event('change'));
            }

            if (langCode === 'ar') {
                document.documentElement.dir = 'rtl';
            } else {
                document.documentElement.dir = 'ltr';
            }
        }

        function addToCart(name, price) {
            let item = cart.find(i => i.name === name);
            if(item) {
                item.quantity += 1;
            } else {
                cart.push({ name: name, price: price, quantity: 1 });
            }
            updateCartUI();
        }

        function removeFromCart(index) {
            cart.splice(index, 1);
            updateCartUI();
        }

        function updateCartUI() {
            let totalCount = cart.reduce((sum, i) => sum + i.quantity, 0);
            let totalSum = cart.reduce((sum, i) => sum + (i.price * i.quantity), 0);
            
            document.getElementById('cartCount').innerText = totalCount;
            document.getElementById('cartTotalSum').innerText = totalSum.toLocaleString();

            let container = document.getElementById('cartItemsContainer');
            if(cart.length === 0) {
                container.innerHTML = '<p style="text-align:center; color:#7f8c8d;">السلة فارغة حالياً.</p>';
            } else {
                container.innerHTML = '';
                cart.forEach((item, index) => {
                    container.innerHTML += `
                        <div class="cart-item">
                            <div class="cart-item-info">
                                <div class="cart-item-title">${item.name} (${item.quantity})</div>
                                <div class="cart-item-price">${(item.price * item.quantity).toLocaleString()} CFA</div>
                            </div>
                            <span class="remove-item" onclick="removeFromCart(${index})">حذف</span>
                        </div>
                    `;
                });
            }

            let userDevice = detectUserDevice();
            let message = "أهلاً، أود طلب المنتجات التالية من متجر الحلول الذكية:\\n\\n";
            cart.forEach(item => {
                message += `• ${item.name} (العدد: ${item.quantity}) - ${(item.price * item.quantity).toLocaleString()} CFA\\n`;
            });
            message += `\\n💵 الإجمالي: ${totalSum.toLocaleString()} CFA`;
            message += `\\n\\n[REF-DEV: ${userDevice}]`;
            
            document.getElementById('whatsappOrderBtn').href = `https://wa.me/${phoneNumber}?text=${encodeURIComponent(message)}`;
        }

        function openCartModal() {
            document.getElementById('cartModal').style.display = 'flex';
        }

        function closeCartModal() {
            document.getElementById('cartModal').style.display = 'none';
        }

        function openModal(src) {
            document.getElementById("fullImage").src = src;
            document.getElementById("imageModal").style.display = "flex";
        }

        function closeModal() {
            document.getElementById("imageModal").style.display = "none";
        }

        function filterCategory(cat, btn) {
            let cards = document.querySelectorAll('.product-card');
            let btns = document.querySelectorAll('.filter-btn');
            
            btns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            cards.forEach(card => {
                if (cat === 'all' || card.getAttribute('data-category') === cat) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
"""

# 6️⃣ الرابط العام للمتجر
@app.route('/')
def home():
    products = Product.query.all()
    return render_template_string(HTML_TEMPLATE, products=products, is_admin=False, phone=PHONE_NUMBER)

# 7️⃣ API لتسجيل جهاز الزائر
@app.route('/api/log-visitor-device', methods=['POST'])
def log_visitor_device():
    data = request.get_json()
    if data and 'device_name' in data:
        log = VisitorLog(device_name=data['device_name'])
        db.session.add(log)
        db.session.commit()
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

# 8️⃣ مسار رفع ملفات CSV
@app.route('/admin/upload-csv', methods=['POST'])
def upload_csv():
    file = request.files.get('csv_file')
    if not file or not file.filename.endswith('.csv'):
        return redirect(url_for('admin', err="يرجى اختيار ملف بصيغة CSV صحيحة."))
    
    try:
        stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
        csv_reader = csv.reader(stream)
        
        first_row = next(csv_reader, None)
        if first_row and first_row[0].strip().lower() in ['name', 'اسم المنتج', 'الاسم']:
            pass
        elif first_row:
            stream.seek(0)
            csv_reader = csv.reader(stream)

        count = 0
        for row in csv_reader:
            if not row or len(row) < 2:
                continue
            
            name = row[0].strip()
            price = float(row[1].strip()) if row[1].strip() else 0.0
            old_price = float(row[2].strip()) if len(row) > 2 and row[2].strip() else None
            category = row[3].strip() if len(row) > 3 and row[3].strip() else "تفعيلات وبوكسات"
            image_url = row[4].strip() if len(row) > 4 and row[4].strip() else None
            is_available = True
            if len(row) > 5 and row[5].strip().lower() in ['false', '0', 'no', 'غير متوفر']:
                is_available = False

            if name and price:
                product = Product(
                    name=name,
                    price=price,
                    old_price=old_price,
                    category=category,
                    image_url=image_url,
                    is_available=is_available
                )
                db.session.add(product)
                count += 1
                
        db.session.commit()
        return redirect(url_for('admin', msg=f"تم استيراد {count} منتج بنجاح!"))
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('admin', err=f"حدث خطأ أثناء معالجة الملف: {str(e)}"))

# 9️⃣ مسار مسح سجلات أجهزة الزوار (إعادة الضبط)
@app.route('/admin/clear-logs')
def clear_logs():
    try:
        VisitorLog.query.delete()
        db.session.commit()
        return redirect(url_for('admin', msg="تم مسح جميع سجلات أجهزة الزوار بنجاح!"))
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('admin', err=f"حدث خطأ أثناء مسح السجلات: {str(e)}"))

# 🔟 لوحة التحكم
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    msg = request.args.get('msg')
    err = request.args.get('err')
    
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        old_price = request.form.get('old_price')
        category = request.form.get('category')
        image_url = request.form.get('image_url')
        is_available = request.form.get('is_available') == '1'
        
        if name and price:
            new_prod = Product(
                name=name, 
                price=float(price), 
                old_price=float(old_price) if old_price else None,
                category=category,
                image_url=image_url, 
                is_available=is_available
            )
            db.session.add(new_prod)
            db.session.commit()
            return redirect(url_for('admin', msg="تم إضافة المنتج بنجاح!"))
    
    products = Product.query.all()
    device_stats = db.session.query(
        VisitorLog.device_name, 
        func.count(VisitorLog.id).label('count')
    ).group_by(VisitorLog.device_name).order_by(text('count DESC')).limit(10).all()

    return render_template_string(
        HTML_TEMPLATE, 
        products=products, 
        is_admin=True, 
        edit_product=None, 
        phone=PHONE_NUMBER,
        device_stats=device_stats,
        msg=msg,
        err=err
    )

# 1️⃣1️⃣ تعديل منتج
@app.route('/admin/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.price = float(request.form.get('price'))
        old_price = request.form.get('old_price')
        product.old_price = float(old_price) if old_price else None
        product.category = request.form.get('category')
        product.image_url = request.form.get('image_url')
        product.is_available = request.form.get('is_available') == '1'
        db.session.commit()
        return redirect(url_for('admin', msg="تم تعديل المنتج بنجاح!"))
    
    products = Product.query.all()
    device_stats = db.session.query(
        VisitorLog.device_name, 
        func.count(VisitorLog.id).label('count')
    ).group_by(VisitorLog.device_name).order_by(text('count DESC')).limit(10).all()

    return render_template_string(
        HTML_TEMPLATE, 
        products=products, 
        is_admin=True, 
        edit_product=product, 
        phone=PHONE_NUMBER,
        device_stats=device_stats
    )

# 1️⃣2️⃣ حذف منتج
@app.route('/admin/delete/<int:product_id>')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin', msg="تم حذف المنتج."))

if __name__ == "__main__":
    app.run()
