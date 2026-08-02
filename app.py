from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    # إنشاء الجدول بالتركيبة الجديدة الصحيحة
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price TEXT NOT NULL,
            image TEXT
        )
    ''')
    
    # إضافة الأعمدة إن كانت مفقودة من قواعد البيانات القديمة
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN description TEXT')
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN image TEXT')
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

# تشغيل الفحص عند الإقلاع
init_db()

@app.route('/')
def index():
    try:
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
                'description': row[2] if len(row) > 2 else '',
                'price': row[3] if len(row) > 3 else '',
                'image': row[4] if len(row) > 4 else ''
            })
        return render_template('index.html', products=products)
    except Exception:
        init_db()
        return render_template('index.html', products=[])

@app.route('/admin')
def admin():
    try:
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
                'description': row[2] if len(row) > 2 else '',
                'price': row[3] if len(row) > 3 else '',
                'image': row[4] if len(row) > 4 else ''
            })
        return render_template('admin.html', products=products)
    except Exception:
        init_db()
        return render_template('admin.html', products=[])

@app.route('/add', methods=['POST'])
def add_product():
    name = request.form.get('name')
    description = request.form.get('description', '')
    price = request.form.get('price')
    image = request.form.get('image', '')
    
    if name and price:
        conn = sqlite3.connect('store.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (name, description, price, image) VALUES (?, ?, ?, ?)',
                       (name, description, price, image))
        conn.commit()
        conn.close()
        
    return redirect('/admin')

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
