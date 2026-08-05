import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# جلب رابط قاعدة البيانات
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

# إنشاء الجداول
with app.app_context():
    db.create_all()

# 1️⃣ الصفحة الرئيسية
@app.route('/')
def home():
    products = Product.query.all()
    if not products:
        return "<h1>المتجر يعمل بنجاح!</h1><p>لا توجد منتجات حالياً. أضف منتج جديد عبر /add-sample</p>"
    
    output = "<h1>قائمة المنتجات:</h1><ul>"
    for p in products:
        output += f"<li>{p.name} - ${p.price}</li>"
    output += "</ul>"
    return output

# 2️⃣ مسار تجريبي لإضافة منتج لقاعدة البيانات
@app.route('/add-sample')
def add_sample():
    new_product = Product(name="شاشة أيفون تجريبية", price=45.0)
    db.session.add(new_product)
    db.session.commit()
    return "تمت إضافة المنتج بنجاح! ارجع للصفحة الرئيسية لرؤيته."

if __name__ == "__main__":
    app.run()
