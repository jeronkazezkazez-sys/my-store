import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# جلب رابط قاعدة البيانات وتعديل البادئة تلقائياً
db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# مثال لجدول المنتجات (تأكد من توائم النماذج لديك)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

# إنشاء الجداول تلقائياً داخل النطاق
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()
