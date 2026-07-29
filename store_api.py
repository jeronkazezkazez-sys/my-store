from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3

app = FastAPI(
    title="متجر الخدمات والمنتجات",
    description="واجهة برمجية وموقع لربط المتجر بصفحة تيك توك والمواقع الأخرى",
    version="1.0.0"
)

# --- 1. إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            item_name TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- 2. نماذج البيانات ---
class OrderCreate(BaseModel):
    customer_name: str
    phone: str
    item_name: str

class ProductCreate(BaseModel):
    name: str
    price: float
    category: str

# --- 3. واجهة الموقع الرئيسية (HTML Frontend) ---
@app.get("/", response_class=HTMLResponse, summary="صفحة المتجر الرئيسية")
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>متجر الخدمات والمنتجات</title>
        <style>
            * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; }
            body { background-color: #f4f7f6; color: #333; padding: 20px; }
            header { text-align: center; padding: 20px 0; background: #111827; color: white; border-radius: 12px; margin-bottom: 25px; }
            header h1 { font-size: 24px; margin-bottom: 5px; }
            header p { font-size: 14px; color: #9ca3af; }
            .container { max-width: 800px; margin: 0 auto; }
            .products-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-bottom: 30px; }
            .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; border: 1px solid #e5e7eb; }
            .card h3 { font-size: 18px; color: #1f2937; margin-bottom: 10px; }
            .card .price { font-size: 22px; color: #059669; font-weight: bold; margin-bottom: 12px; }
            .card .category { display: inline-block; background: #e0e7ff; color: #3730a3; font-size: 12px; padding: 4px 10px; border-radius: 12px; margin-bottom: 12px; }
            .btn-order { background-color: #25d366; color: white; border: none; padding: 10px 15px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%; text-decoration: none; display: inline-block; }
            .btn-order:hover { background-color: #1eb956; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>📱 متجر الخدمات والمنتجات</h1>
                <p>أهلاً بكم! تصفح خدماتنا ومنتجاتنا واطلب مباشرة</p>
            </header>

            <h2 style="margin-bottom: 15px;">المنتجات والخدمات المتاحة</h2>
            <div id="products-list" class="products-grid">
                <p>جاري تحميل المنتجات...</p>
            </div>
        </div>

        <script>
            async function fetchProducts() {
                const container = document.getElementById('products-list');
                try {
                    const response = await fetch('/api/products');
                    const products = await response.json();
                    container.innerHTML = '';

                    if (!products || products.length === 0) {
                        container.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #6b7280;">لا توجد منتجات متاحة حالياً.</p>';
                        return;
                    }

                    products.forEach(p => {
                        const card = document.createElement('div');
                        card.className = 'card';
                        card.innerHTML = `
                            <span class="category">${p.category}</span>
                            <h3>${p.name}</h3>
                            <div class="price">$${p.price}</div>
                            <button class="btn-order" onclick="orderProduct('${p.name}')">طلب عبر الواتساب</button>
                        `;
                        container.appendChild(card);
                    });
                } catch (err) {
                    console.error(err);
                    container.innerHTML = '<p style="color: red;">حدث خطأ أثناء جلب المنتجات.</p>';
                }
            }

            function orderProduct(itemName) {
                const phone = "218000000000"; 
                const msg = encodeURIComponent(`مرحباً، أرغب في طلب المنتج/الخدمة التالية: ${itemName}`);
                window.open(`https://wa.me/${phone}?text=${msg}`, '_blank');
            }

            fetchProducts();
        </script>
    </body>
    </html>
    """

# --- 4. روابط الـ API ---
@app.get("/api/products", summary="جلب جميع المنتجات")
def get_products():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, category FROM products")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "price": r[2], "category": r[3]} for r in rows]

@app.post("/api/products", summary="إضافة منتج جديد")
def add_product(product: ProductCreate):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price, category) VALUES (?, ?, ?)", (product.name, product.price, product.category))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "تم إضافة المنتج بنجاح"}

@app.post("/api/orders", summary="إرسال طلب جديد")
def create_order(order: OrderCreate):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (customer_name, phone, item_name) VALUES (?, ?, ?)", (order.customer_name, order.phone, order.item_name))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "تم استلام الطلب وتسجيله بنجاح!"} 