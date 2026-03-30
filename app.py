from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, make_response
import sqlite3, csv, io, hashlib, secrets, os
from datetime import datetime, date, time

app = Flask(__name__)

# Persist secret key
_SK_FILE = '.secret_key'
if os.path.exists(_SK_FILE):
    app.secret_key = open(_SK_FILE).read().strip()
else:
    app.secret_key = secrets.token_hex(32)
    open(_SK_FILE, 'w').write(app.secret_key)

DATABASE = 'database.db'

def hash_password(pw):
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 260000)
    return f"pbkdf2:{salt}:{dk.hex()}"

def check_password(stored, provided):
    try:
        _, salt, dk_hex = stored.split(':', 2)
        dk = hashlib.pbkdf2_hmac('sha256', provided.encode(), salt.encode(), 260000)
        return dk.hex() == dk_hex
    except Exception:
        return False

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    with open('schema.sql') as f:
        conn.executescript(f.read())
    conn.commit()
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        conn.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",
                     ('admin', hash_password('admin123'), 'admin'))
        conn.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",
                     ('kitchen', hash_password('kitchen123'), 'kitchen_staff'))
        conn.commit()
    if conn.execute("SELECT COUNT(*) FROM food_items").fetchone()[0] == 0:
        items = [
            ('Chapati','Breakfast',30),('Mandazi','Breakfast',20),('Uji','Breakfast',40),
            ('Boiled Eggs','Breakfast',30),('Chapati + Tea','Combos',60),
            ('Rice + Stew Combo','Combos',150),('Ugali + Sukuma Combo','Combos',100),
            ('Beef Stew','Meat',150),('Chicken','Meat',200),('Fried Fish','Meat',180),
            ('Nyama Choma','Meat',250),('Rice','Main Food',80),('Ugali','Main Food',60),
            ('Pilau','Main Food',120),('Githeri','Main Food',80),
            ('Cake Slice','Sweet Categories',80),('Doughnut','Sweet Categories',30),
            ('Maandazi Tamu','Sweet Categories',25),('Mango Milkshake','Drinks',100),
            ('Tea','Drinks',30),('Soda','Drinks',60),('Water','Drinks',30),
            ('Extra Sauce','Add-ons',20),('Kachumbari','Add-ons',30),('Avocado','Add-ons',40),
        ]
        conn.executemany("INSERT INTO food_items (name,category,price) VALUES (?,?,?)", items)
        conn.commit()
    conn.close()

CATEGORIES = ['Breakfast','Combos','Meat','Main Food','Sweet Categories','Drinks','Add-ons']

# ── CUSTOMER ──────────────────────────────────────────────────────────────────
@app.route('/')
def index(): return render_template('index.html')

@app.route('/landing')
def landing(): return render_template('landing.html')

@app.route('/menu')
def menu():
    conn = get_db()
    items = conn.execute("SELECT * FROM food_items ORDER BY category,name").fetchall()
    conn.close()
    cart = session.get('cart', {})
    return render_template('menu.html', items=items, categories=CATEGORIES,
                           cart_count=sum(cart.values()))

@app.route('/cart')
def cart():
    c = session.get('cart', {})
    cart_items, total = [], 0
    if c:
        conn = get_db()
        for fid, qty in c.items():
            item = conn.execute("SELECT * FROM food_items WHERE id=?", (fid,)).fetchone()
            if item:
                sub = item['price'] * qty; total += sub
                cart_items.append({'id': fid,'name':item['name'],'price':item['price'],'qty':qty,'subtotal':sub})
        conn.close()
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    fid = str(request.form.get('food_id'))
    c = session.get('cart', {}); c[fid] = c.get(fid, 0) + 1
    session['cart'] = c; session.modified = True
    return jsonify({'success': True, 'cart_count': sum(c.values())})

@app.route('/update-cart', methods=['POST'])
def update_cart():
    fid = str(request.form.get('food_id')); action = request.form.get('action')
    c = session.get('cart', {})
    if action == 'increase': c[fid] = c.get(fid, 0) + 1
    elif action == 'decrease':
        if c.get(fid, 0) > 1: c[fid] -= 1
        else: c.pop(fid, None)
    elif action == 'remove': c.pop(fid, None)
    session['cart'] = c; session.modified = True
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    c = session.get('cart', {})
    if not c: return redirect(url_for('menu'))
    cart_items, total = [], 0
    conn = get_db()
    for fid, qty in c.items():
        item = conn.execute("SELECT * FROM food_items WHERE id=?", (fid,)).fetchone()
        if item:
            sub = item['price']*qty; total += sub
            cart_items.append({'name':item['name'],'price':item['price'],'qty':qty,'subtotal':sub})
    conn.close()
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/place-order', methods=['POST'])
def place_order():
    try:
        name = request.form.get('customer_name','').strip()
        phone = request.form.get('phone_number','').strip()
        table = request.form.get('table_number','').strip()
        if not (name and phone and table): return redirect(url_for('payment_failed'))
        c = session.get('cart', {})
        if not c: return redirect(url_for('menu'))
        conn = get_db(); total = 0; items_data = []
        for fid, qty in c.items():
            item = conn.execute("SELECT * FROM food_items WHERE id=?", (fid,)).fetchone()
            if item: total += item['price']*qty; items_data.append((int(fid), qty))
        cur = conn.execute("INSERT INTO orders (customer_name,phone_number,table_number,total_amount) VALUES (?,?,?,?)",
                           (name, phone, table, total))
        oid = cur.lastrowid
        for fid, qty in items_data:
            conn.execute("INSERT INTO order_items (order_id,food_id,quantity) VALUES (?,?,?)", (oid,fid,qty))
        conn.commit(); conn.close()
        session.pop('cart', None); session.modified = True
        return redirect(url_for('payment_success', order_id=oid))
    except Exception as e:
        print(f"Order error: {e}"); return redirect(url_for('payment_failed'))

@app.route('/payment-success/<int:order_id>')
def payment_success(order_id):
    conn = get_db(); order = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone(); conn.close()
    if not order: return redirect(url_for('index'))
    return render_template('payment_success.html', order=order)

@app.route('/payment-failed')
def payment_failed(): return render_template('payments_not_successful.html')

@app.route('/my-orders')
def my_orders(): return render_template('my_orders.html')

@app.route('/feedback')
def feedback(): return render_template('feedback.html')

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    rating = request.form.get('rating'); comment = request.form.get('comment','').strip()
    if not rating: flash('Please select a rating.','error'); return redirect(url_for('feedback'))
    conn = get_db(); conn.execute("INSERT INTO feedback (rating,comment) VALUES (?,?)", (int(rating), comment or None))
    conn.commit(); conn.close(); flash('Thank you for your feedback! 🌟','success')
    return redirect(url_for('landing'))

# ── KITCHEN ───────────────────────────────────────────────────────────────────
@app.route('/kitchen-login', methods=['GET','POST'])
def kitchen_login():
    if request.method == 'POST':
        u = request.form.get('username','').strip(); p = request.form.get('password','')
        conn = get_db(); user = conn.execute("SELECT * FROM users WHERE username=?", (u,)).fetchone(); conn.close()
        if user and check_password(user['password'], p) and user['role'] in ('admin','kitchen_staff'):
            session.update({'user_id':user['id'],'username':user['username'],'role':user['role']})
            return redirect(url_for('kitchen'))
        flash('Invalid credentials','error')
    return render_template('kitchen_login.html')

@app.route('/kitchen')
def kitchen():
    if session.get('role') not in ('admin','kitchen_staff'): return redirect(url_for('kitchen_login'))
    return render_template('kitchen.html', username=session.get('username'))

@app.route('/update-order-status', methods=['POST'])
def update_order_status():
    if session.get('role') not in ('admin','kitchen_staff'): return jsonify({'error':'Unauthorized'}), 401
    oid = request.form.get('order_id'); s = request.form.get('status')
    if s not in ['Pending','Preparing','Ready','Served','Cancelled']: return jsonify({'error':'Invalid'}), 400
    conn = get_db(); conn.execute("UPDATE orders SET status=? WHERE id=?", (s, oid)); conn.commit(); conn.close()
    return jsonify({'success': True})

@app.route('/kitchen-logout')
def kitchen_logout(): session.clear(); return redirect(url_for('kitchen_login'))

# ── ADMIN ─────────────────────────────────────────────────────────────────────
@app.route('/admin-login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        u = request.form.get('username','').strip(); p = request.form.get('password','')
        conn = get_db(); user = conn.execute("SELECT * FROM users WHERE username=?", (u,)).fetchone(); conn.close()
        if user and check_password(user['password'], p) and user['role'] == 'admin':
            session.update({'user_id':user['id'],'username':user['username'],'role':user['role']})
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials','error')
    return render_template('admin_login.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    conn = get_db(); today = date.today().isoformat()
    ts = conn.execute("SELECT COALESCE(SUM(total_amount),0) FROM orders WHERE DATE(created_at)=? AND status='Served'",(today,)).fetchone()[0]
    to = conn.execute("SELECT COUNT(*) FROM orders WHERE DATE(created_at)=?",(today,)).fetchone()[0]
    ak = conn.execute("SELECT COUNT(*) FROM orders WHERE status IN ('Preparing','Ready') AND payment_status='Paid'").fetchone()[0]
    pp = conn.execute("SELECT * FROM orders WHERE payment_status='Unpaid' ORDER BY created_at DESC").fetchall()
    rs = conn.execute("SELECT * FROM orders WHERE status='Served' ORDER BY created_at DESC LIMIT 10").fetchall()
    conn.close()
    return render_template('admin_dashboard.html', today_sales=ts, today_orders=to,
        active_kitchen=ak, pending_payments=pp, recent_served=rs, username=session.get('username'))

@app.route('/admin-food')
def admin_food():
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    conn = get_db(); items = conn.execute("SELECT * FROM food_items ORDER BY category,name").fetchall(); conn.close()
    return render_template('admin_food.html', items=items, categories=CATEGORIES, username=session.get('username'))

@app.route('/admin-food/add', methods=['POST'])
def admin_food_add():
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    n=request.form.get('name','').strip(); cat=request.form.get('category'); p=request.form.get('price'); av=1 if request.form.get('available')=='1' else 0
    if n and cat and p:
        conn=get_db(); conn.execute("INSERT INTO food_items (name,category,price,available) VALUES (?,?,?,?)",(n,cat,float(p),av)); conn.commit(); conn.close()
        flash('Food item added!','success')
    return redirect(url_for('admin_food'))

@app.route('/admin-food/edit/<int:item_id>', methods=['POST'])
def admin_food_edit(item_id):
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    n=request.form.get('name','').strip(); cat=request.form.get('category'); p=request.form.get('price'); av=1 if request.form.get('available')=='1' else 0
    conn=get_db(); conn.execute("UPDATE food_items SET name=?,category=?,price=?,available=? WHERE id=?",(n,cat,float(p),av,item_id)); conn.commit(); conn.close()
    flash('Food item updated!','success'); return redirect(url_for('admin_food'))

@app.route('/admin-food/delete/<int:item_id>', methods=['POST'])
def admin_food_delete(item_id):
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    conn=get_db(); conn.execute("DELETE FROM food_items WHERE id=?",(item_id,)); conn.commit(); conn.close()
    flash('Food item deleted.','success'); return redirect(url_for('admin_food'))

@app.route('/admin-food/toggle/<int:item_id>', methods=['POST'])
def admin_food_toggle(item_id):
    if session.get('role') != 'admin': return jsonify({'error':'Unauthorized'}), 401
    conn=get_db(); item=conn.execute("SELECT available FROM food_items WHERE id=?",(item_id,)).fetchone()
    nv=0 if item['available'] else 1; conn.execute("UPDATE food_items SET available=? WHERE id=?",(nv,item_id)); conn.commit(); conn.close()
    return jsonify({'success':True,'available':nv})

@app.route('/admin-sales')
def admin_sales():
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    conn=get_db()
    orders=conn.execute("SELECT o.*,GROUP_CONCAT(f.name||' x'||oi.quantity,', ') as items FROM orders o LEFT JOIN order_items oi ON o.id=oi.order_id LEFT JOIN food_items f ON oi.food_id=f.id WHERE o.status='Served' GROUP BY o.id ORDER BY o.created_at DESC").fetchall()
    tr=conn.execute("SELECT COALESCE(SUM(total_amount),0) FROM orders WHERE status='Served'").fetchone()[0]; conn.close()
    return render_template('admin_sales.html', orders=orders, total_revenue=tr, username=session.get('username'))

@app.route('/admin-sales/export-csv')
def export_csv():
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    conn=get_db()
    orders=conn.execute("SELECT o.id,o.customer_name,o.table_number,o.total_amount,o.created_at,GROUP_CONCAT(f.name||' x'||oi.quantity,', ') as items FROM orders o LEFT JOIN order_items oi ON o.id=oi.order_id LEFT JOIN food_items f ON oi.food_id=f.id WHERE o.status='Served' GROUP BY o.id ORDER BY o.created_at DESC").fetchall()
    conn.close(); buf=io.StringIO(); w=csv.writer(buf)
    w.writerow(['Date','Order #','Customer','Table','Items','Amount (KES)'])
    for o in orders: w.writerow([o['created_at'],o['id'],o['customer_name'],o['table_number'],o['items'],o['total_amount']])
    fname=f"nova_eatery_sales_{date.today().isoformat()}.csv"
    resp=make_response(buf.getvalue()); resp.headers['Content-Disposition']=f'attachment; filename={fname}'; resp.headers['Content-Type']='text/csv'
    return resp

@app.route('/admin-payment-confirmation')
def admin_payment_confirmation():
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    conn=get_db()
    pending=conn.execute("SELECT * FROM orders WHERE payment_status='Unpaid' ORDER BY created_at DESC").fetchall()
    today=date.today().isoformat()
    confirmed=conn.execute("SELECT o.*,p.confirmed_at FROM orders o JOIN payments p ON o.id=p.order_id WHERE DATE(p.confirmed_at)=? ORDER BY p.confirmed_at DESC",(today,)).fetchall()
    conn.close()
    return render_template('admin_payment_confirmation.html', pending=pending, confirmed=confirmed, username=session.get('username'))

@app.route('/admin-feedbacks')
def admin_feedbacks():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    conn = get_db()
    # Use feedbackid instead of id
    feedbacks = conn.execute("""
        SELECT feedbackid, rating, comment, created_at 
        FROM feedback 
        ORDER BY created_at DESC
    """).fetchall()
    conn.close()
    
    total_feedbacks = len(feedbacks)
    avg_rating = 0
    rating_distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    
    if total_feedbacks > 0:
        total_rating = sum(f['rating'] for f in feedbacks)
        avg_rating = round(total_rating / total_feedbacks, 1)
        
        for f in feedbacks:
            rating_distribution[f['rating']] += 1
    
    return render_template('admin_feedbacks.html', 
                         feedbacks=feedbacks,
                         total_feedbacks=total_feedbacks,
                         avg_rating=avg_rating,
                         rating_distribution=rating_distribution,
                         username=session.get('username'))

@app.route('/confirm-payment/<int:order_id>', methods=['POST'])
def confirm_payment(order_id):
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    conn=get_db(); conn.execute("UPDATE orders SET payment_status='Paid' WHERE id=?",(order_id,))
    conn.execute("INSERT INTO payments (order_id,confirmed_by,confirmed_at) VALUES (?,?,datetime('now'))",(order_id,session.get('user_id'))); conn.commit(); conn.close()
    flash('Payment confirmed! Order sent to kitchen. ✅','success')
    return redirect(request.referrer or url_for('admin_dashboard'))

@app.route('/admin-logout')
def admin_logout(): session.clear(); return redirect(url_for('admin_login'))

# ── API ────────────────────────────────────────────────────────────────────────
@app.route('/api/orders')
def api_orders():
    if session.get('role') not in ('admin','kitchen_staff'): return jsonify({'error':'Unauthorized'}), 401
    conn=get_db()
    orders=conn.execute("SELECT id,customer_name,phone_number,table_number,total_amount,status,created_at FROM orders WHERE payment_status='Paid' AND status NOT IN ('Served','Cancelled') ORDER BY created_at DESC").fetchall()
    result=[]
    for o in orders:
        items=conn.execute("SELECT f.name,oi.quantity as qty FROM order_items oi JOIN food_items f ON oi.food_id=f.id WHERE oi.order_id=?",(o['id'],)).fetchall()
        result.append({'id':o['id'],'customer_name':o['customer_name'],'phone_number':o['phone_number'],'table_number':o['table_number'],'total_amount':o['total_amount'],'status':o['status'],'created_at':o['created_at'],'items':[{'name':i['name'],'qty':i['qty']} for i in items]})
    conn.close(); return jsonify(result)

@app.route('/api/order-status/<int:order_id>')
def api_order_status(order_id):
    conn=get_db(); o=conn.execute("SELECT id,status,payment_status FROM orders WHERE id=?",(order_id,)).fetchone(); conn.close()
    if not o: return jsonify({'error':'Not found'}), 404
    return jsonify({'id':o['id'],'status':o['status'],'payment_status':o['payment_status']})

@app.route('/api/my-orders')
def api_my_orders():
    phone=request.args.get('phone','').strip()
    if not phone: return jsonify([])
    conn=get_db(); orders=conn.execute("SELECT * FROM orders WHERE phone_number=? ORDER BY created_at DESC",(phone,)).fetchall(); conn.close()
    return jsonify([{'id':o['id'],'table_number':o['table_number'],'total_amount':o['total_amount'],'status':o['status'],'created_at':o['created_at']} for o in orders])

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
