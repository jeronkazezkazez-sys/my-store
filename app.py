import os
import urllib.parse
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

WHATSAPP_NUMBER = "22791697671"  # ضع رقمك هنا

# إعداد قاعدة البيانات
db_url = os.environ.get('DATABASE_URL', 'sqlite:///store.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------------------------------------------------------
# نموذج قاعدة البيانات
# -------------------------------------------------------------------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)

# دالة تقسيم روابط الصور المتعددة
def parse_images(image_url_str):
    if not image_url_str:
        return ['https://via.placeholder.com/300']
    images = [url.strip() for url in str(image_url_str).split(',') if url.strip()]
    return images if images else ['https://via.placeholder.com/300']

# -------------------------------------------------------------------
# المسارات (Routes)
# -------------------------------------------------------------------

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

# مسار استقبال إضافة المنتجات (يدعم كل المسميات المحتملة)
@app.route('/add-product', methods=['POST'])
@app.route('/add_product', methods=['POST'])
@app.route('/api/add-product', methods=['POST'])
def add_product():
    # استقبال البيانات سواء كانت من Form أو JSON
    title = request.form.get('title') or (request.json and request.json.get('title'))
    price = request.form.get('price') or (request.json and request.json.get('price'))
    image_url = request.form.get('image_url') or (request.json and request.json.get('image_url'))
    category = request.form.get('category') or (request.json and request.json.get('category'))
    description = request.form.get('description') or (request.json and request.json.get('description'))

    if not title or not price:
        return "بيانات المنتج غير اكتمال", 400

    new_product = Product(
        title=title,
        price=float(price),
        image_url=image_url,
        category=category,
        description=description
    )
    db.session.add(new_product)
    db.session.commit()

    # إذا كان الطلب من نموذج عادي نعيد توجيهه للوحة التحكم
    if request.form:
        return redirect(url_for('admin'))
    return jsonify({'status': 'success', 'message': 'Product added successfully!'})

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

@app.route('/buy/<int:product_id>')
def buy_product(product_id):
    p = Product.query.get_or_404(product_id)
    message = f"مرحباً، أريد طلب المنتج التالي:\n- الاسم: {p.title}\n- السعر: {p.price}"
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={encoded_message}"
    return redirect(whatsapp_url)

# -------------------------------------------------------------------
# التهيئة والتحديث
# -------------------------------------------------------------------
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database note: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
