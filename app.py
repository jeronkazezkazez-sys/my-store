from flask import Flask, render_template, request, redirect
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)

# الحصول على رابط قاعدة البيانات من بيئة Render أو استخدام الإعداد الافتراضي
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if DATABASE_URL:
        # إصلاح بادئة الرابط إن كانت postgres:// لتصبح postgresql://
        url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        conn = psycopg2.connect(url, sslmode='require')
    else:
        # احتياطي محلي
        import sqlite3
        conn = sqlite3.connect('store_v2.db')
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    if DATABASE_URL:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price TEXT NOT NULL,
                image TEXT,
                is_available INTEGER DEFAULT 1
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price TEXT NOT NULL,
                image TEXT,
                is_available INTEGER DEFAULT 1
            )
        ''')
    conn.commit()
    cursor.close()
    conn.close()

try:
    init_db()
except Exception as e:
    print("DB Init Error:", e)

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, description, price, image, is_available FROM products ORDER BY id DESC')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    products = []
    for row in rows:
        products.append({
            'id': row[0],
            'name': row[1],
            'description': row[2] if row[2] else '',
            'price': row[3] if row[3] else '',
            'image': row[4] if row[4] else '',
            'is_available': row[5] if len(row) > 5 and row[5] is not None else 1
        })
    return render_template('index.html', products=products)

@app.route('/admin')
def admin():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, description, price, image, is_available FROM products ORDER BY id DESC')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    products = []
    for row in rows:
        products.append({
            'id': row[0],
            'name': row[1],
            'description': row[2] if row[2] else '',
            'price': row[3] if row[3] else '',
            'image': row[4] if row[4] else '',
            'is_available': row[5] if len(row) > 5 and row[5] is not None else 1
        })
    return render_template('admin.html', products=products)

@app.route('/add', methods=['POST'])
def add_product():
    name = request.form.get('name')
    description = request.form.get('description', '')
    price = request.form.get('price')
    image = request.form.get('image', '')
    
    if name and price:
        conn = get_db_connection()
        cursor = conn.cursor()
        if DATABASE_URL:
            cursor.execute('INSERT INTO products (name, description, price, image, is_available) VALUES (%s, %s, %s, %s, 1)',
                           (name, description, price, image))
        else:
            cursor.execute('INSERT INTO products (name, description, price, image, is_available) VALUES (?, ?, ?, ?, 1)',
                           (name, description, price, image))
        conn.commit()
        cursor.close()
        conn.close()
        
    return redirect('/admin')

@app.route('/toggle/<int:product_id>')
def toggle_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if DATABASE_URL:
        cursor.execute('UPDATE products SET is_available = CASE WHEN is_available = 1 THEN 0 ELSE 1 END WHERE id = %s', (product_id,))
    else:
        cursor.execute('UPDATE products SET is_available = CASE WHEN is_available = 1 THEN 0 ELSE 1 END WHERE id = ?', (product_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/admin')

@app.route('/delete/<int:product_id>')
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if DATABASE_URL:
        cursor.execute('DELETE FROM products WHERE id = %s', (product_id,))
    else:
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/admin')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
