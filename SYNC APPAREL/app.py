from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

users = {}

products = [
    {
        'id': 1,
        'name': 'Элегантное платье',
        'price': 2990,
        'image': '/static/images/dress1.jpg',
        'category': 'Платья',
        'description': 'Прекрасное платье для особых случаев'
    },
    {
        'id': 2,
        'name': 'Джинсы',
        'price': 1890,
        'image': '/db.db',
        'category': 'Джинсы',
        'description': 'Удобные джинсы на каждый день'
    },
    {
        'id': 3,
        'name': 'Блузка с рюшами',
        'price': 1290,
        'image': '/',
        'category': 'Блузки',
        'description': 'Женственная блузка для прогулок'
    },
    {
        'id': 4,
        'name': 'Футболка базовая',
        'price': 790,
        'image': '/',
        'category': 'Футболки',
        'description': 'Универсальная футболка на каждый день'
    },
    {
        'id': 5,
        'name': 'Кардиган',
        'price': 2390,
        'image': '/',
        'category': 'Верхняя одежда',
        'description': 'Теплый кардиган для прохладных дней'
    }
]

def get_cart():
    if 'cart' not in session:
        session['cart'] = []
    return session['cart']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/catalog')
def catalog():
    category = request.args.get('category', 'Все')
    if category == 'Все':
        filtered_products = products
    else:
        filtered_products = [p for p in products if p['category'] == category]
    
    categories = ['Все'] + list(set(p['category'] for p in products))
    return render_template('catalog.html', 
                         products=filtered_products, 
                         categories=categories,
                         selected_category=category)

@app.route('/cart')
def cart():
    cart_items = get_cart()
    cart_products = []
    total = 0
    
    for item in cart_items:
        product = next((p for p in products if p['id'] == item['product_id']), None)
        if product:
            product['quantity'] = item['quantity']
            product['subtotal'] = product['price'] * item['quantity']
            total += product['subtotal']
            cart_products.append(product)
    
    return render_template('cart.html', cart=cart_products, total=total)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = int(request.json['product_id'])
    quantity = int(request.json.get('quantity', 1))
    
    cart = get_cart()
    
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            break
    else:
        cart.append({'product_id': product_id, 'quantity': quantity})
    
    session.modified = True
    return jsonify({'success': True, 'cart_count': len(cart)})

@app.route('/update_cart', methods=['POST'])
def update_cart():
    product_id = int(request.json['product_id'])
    quantity = int(request.json['quantity'])
    
    cart = get_cart()
    
    if quantity <= 0:
        cart[:] = [item for item in cart if item['product_id'] != product_id]
    else:
        for item in cart:
            if item['product_id'] == product_id:
                item['quantity'] = quantity
                break
    
    session.modified = True
    return jsonify({'success': True})

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    product_id = int(request.json['product_id'])
    
    cart = get_cart()
    cart[:] = [item for item in cart if item['product_id'] != product_id]
    
    session.modified = True
    return jsonify({'success': True})

@app.route('/profile')
def profile():
    if 'user' in session:
        return render_template('profile.html', user=session['user'])
    else:
        return redirect(url_for('auth'))

@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    
    if email in users:
        flash('Пользователь с такой почтой уже существует!', 'error')
        return redirect(url_for('auth'))
    
    users[email] = {'name': name, 'email': email, 'password': password}
    session['user'] = users[email]
    flash('Регистрация прошла успешно!', 'success')
    return redirect(url_for('profile'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    if email in users and users[email]['password'] == password:
        session['user'] = users[email]
        flash('Вход выполнен успешно!', 'success')
        return redirect(url_for('profile'))
    else:
        flash('Неверная почта или пароль!', 'error')
        return redirect(url_for('auth'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/reviews')
def reviews():
    return render_template('page.html', title='Отзывы')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

if __name__ == '__main__':
    app.run(debug=True)

