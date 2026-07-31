from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# دالة للاتصال بقاعدة البيانات
def get_db_connection():
    conn = sqlite3.connect('store.db')
    conn.row_factory = sqlite3.Row
    return conn

# إنشاء جدول المنتجات تلقائياً
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# الصفحة الرئيسية للمتجر
@app.route('/')
def home():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('index.html', products=products)

# صفحة لوحة التحكم لإدارة المنتجات
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        category = request.form['category']
        description = request.form['description']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO products (name, price, category, description) VALUES (?, ?, ?, ?)',
                     (name, price, category, description))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))
        
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('admin.html', products=products)

# حذف منتج
@app.route('/delete/<int:id>', methods=['POST'])
def delete_product(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))