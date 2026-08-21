import os
import urllib.parse
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# -------------------------------------------------------------------
# رقم الهاتف الخاص باستلام الطلبات على الواتساب (مع الرمز الدولي)
# -------------------------------------------------------------------
WHATSAPP_NUMBER = "22791697671"  # غيّره إلى رقمك

# إعداد قاعدة البيانات
db_url = os.environ.get('DATABASE_URL', 'sqlite:///store.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------------------------------------------------------
# نموذج قاعدة البيانات للمنتجات
# -------------------------------------------------------------------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)

# -------------------------------------------------------------------
# دالة تقسيم روابط الصور المتعددة
# -------------------------------------------------------------------
def parse_images(image_url_str):
    if not image_url_str:
        return ['https://via.placeholder.com/300']
    images = [url.strip() for url in str(image_url_str).split(',') if url.strip()]
    return images if images else ['https://via.placeholder.com/300']

# -------------------------------------------------------------------
# المسارات (Routes)
# -------------------------------------------------------------------

# الصفحة الرئيسية للمتجر
@app.route('/')
def index():
    try:
        products_query = Product.query.all()
    except Exception:
        products_query = []
        
    products = []
    for p in products_query:
        products.append({
            'id': p.id,
            'title': p.title,
            'price': p.price,
            'image_url': p.image_url,
            'images': parse_images(p.image_url),
            'category': p.category,
            'description': p.description
        })
        
    return render_template('index.html', products=products, whatsapp_number=WHATSAPP_NUMBER)

# صفحة لوحة التحكم / إدارة المنتجات
@app.route('/admin')
def admin():
    try:
        products_query = Product.query.all()
    except Exception:
        products_query = []
        
    products = []
    for p in products_query:
        products.append({
            'id': p.id,
            'title': p.title,
            'price': p.price,
            'image_url': p.image_url,
            'images': parse_images(p.image_url),
            'category': p.category,
            'description': p.description
        })
    return render_template('admin.html', products=products)

# تفاصيل المنتج
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    p = Product.query.get_or_404(product_id)
    product = {
        'id': p.id,
        'title': p.title,
        'price': p.price,
        'image_url': p.image_url,
        'images': parse_images(p.image_url),
        'category': p.category,
        'description': p.description
    }
    return render_template('product.html', product=product, whatsapp_number=WHATSAPP_NUMBER)

# زر الشراء المباشر والتحويل إلى الواتساب
@app.route('/buy/<int:product_id>')
def buy_product(product_id):
    p = Product.query.get_or_404(product_id)
    message = f"مرحباً، أريد طلب المنتج التالي:\n- الاسم: {p.title}\n- السعر: {p.price}"
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_message}"
    return redirect(whatsapp_url)

# مسار إضافة منتج جديد (من لوحة التحكم أو API)
@app.route('/api/add-product', methods=['POST'])
def add_product():
    data = request.json or request.form
    new_product = Product(
        title=data.get('title'),
        price=float(data.get('price', 0)),
        image_url=data.get('image_url'),
        category=data.get('category'),
        description=data.get('description')
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Product added successfully!'})

# مسار حذف منتج
@app.route('/api/delete-product/<int:product_id>', methods=['DELETE', 'POST'])
def delete_product(product_id):
    p = Product.query.get_or_404(product_id)
    db.session.delete(p)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Product deleted successfully!'})

# -------------------------------------------------------------------
# تهيئة الجداول
# -------------------------------------------------------------------
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database initialization note: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
