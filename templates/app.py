from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

# إنشاء أو الاتصال بقاعدة البيانات
def init_db():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    
    # إنشاء الجدول لو مش موجود
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price TEXT NOT NULL,
            image TEXT
        )
    ''')
    
    # محاولة إضافة عمود description لو كان الجدول قديم ومقفيش العمود
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN description TEXT")
    except Exception:
        pass

    conn.commit()
    conn.close()

init_db()

# الصفحة الرئيسية للزبائن
@app.route('/')
def index():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, description, price, image FROM products')
    rows = cursor.fetchall()
    conn.close()
    
    products = []
    for row in rows:
        products.append({
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'price': row[3],
            'image': row[4]
        })
        
    return render_template('index.html', products=products)

# صفحة لوحة التحكم للإدارة
@app.route('/admin')
def admin():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, description, price, image FROM products')
    rows = cursor.fetchall()
    conn.close()
    
    products = []
    for row in rows:
        products.append({
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'price': row[3],
            'image': row[4]
        })
        
    return render_template('admin.html', products=products)

# إضافة منتج جديد
@app.route('/add', methods=['POST'])
def add_product():
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    image = request.form.get('image')
    
    if name and price:
        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (name, description, price, image) VALUES (?, ?, ?, ?)',
                       (name, description, price, image))
        conn.commit()
        conn.close()
        
    return redirect('/admin')

# حذف منتج
@app.route('/delete/<int:product_id>')
def delete_product(product_id):
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    
    return redirect('/admin')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)