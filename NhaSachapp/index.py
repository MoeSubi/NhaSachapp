import math
import cloudinary.uploader
from flask import render_template, redirect, url_for, session, jsonify, request
from NhaSachapp import app, login
from flask_login import login_user, logout_user, login_required
from NhaSachapp.admin import *
import utils


@app.route("/")
def index():
    kw = request.args.get('keyword')
    cate_id = request.args.get('category_id')
    counter = utils.count_products()
    page = request.args.get('page', 1)
    products = utils.load_products(cate_id=cate_id, kw=kw, page=int(page))
    return render_template('index.html',
                           products=products,
                           pages=math.ceil(counter/app.config['PAGE_SIZE']))


@app.route('/admin-login', methods=['post'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = utils.check_login(username, password)
    if user:
        login_user(user=user)

    return redirect('/admin')


@login.user_loader
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)


@app.route('/register', methods=['get', 'post'])
def user_register():
    err_msg = ""
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        avatar_path = None
        try:
            if password.strip().__eq__(confirm.strip()):
                avatar = request.files.get('avatar')

                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']
                utils.add_user(name=name, username=username, password=password, email=email, avatar=avatar_path)
                return redirect(url_for('user_signin'))
            else:
                err_msg = 'Mat khau khong giong nhau'
        except Exception as ex:
            err_msg = 'he thong dang co loi' + str(ex)

    return render_template('register.html', err_msg=err_msg)


@app.route('/user-login', methods=['get', 'post'])
def user_signin():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = utils.check_login(username=username, password=password)
        if user:
            login_user(user=user)

            if 'product_id' in request.args:
                return redirect(url_for(request.args.get('next', 'index'), product_id=request.args['product_id']))

            return redirect(url_for(request.args.get('next', 'index')))
        else:
            err_msg = 'Username hoặc Password sai!'

    return render_template('login.html',
                           err_msg=err_msg)


@app.context_processor
def common_response():
    return {
        'categories': utils.load_categories(),
        'cart_stats': utils.count_cart(session.get('cart'))
    }


@app.route('/user-logout')
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))


@app.route('/api/add-cart', methods=['post'])
def add_to_cart():
    data = request.json
    id = str(data.get('id'))
    name = data.get('name')
    price = data.get('price')
    cart = session.get('cart')

    if not cart:
        cart = {}

    if id in cart:
        cart[id]['quantity'] = cart[id]['quantity'] + 1
    else:
        cart[id] = {
            'id': id,
            'name': name,
            'price': price,
            'quantity': 1
        }
    session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/api/update-cart', methods=['put'])
def update_cart():
    data = request.json
    id = str(data.get('id'))
    quantity = data.get('quantity')

    cart = session.get('cart')
    if cart and id in cart:
        cart[id]['quantity'] = quantity
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/api/delete-cart/<product_id>', methods=['delete'])
def delete_cart(product_id):
    cart = session.get('cart')

    if cart and product_id in cart:
        del cart[product_id]
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/products/<int:product_id>')
def product_detail(product_id):
    product = utils.get_product_by_id(product_id=product_id)
    counter = utils.count_comments(product_id=product_id)

    return render_template('product_detail.html', product=product,
                           pages=math.ceil(counter/app.config['COMMENT_SIZE']))


@app.route('/cart/')
def cart():
    return render_template('cart.html',
                           stats=utils.count_cart(session.get('cart')))


@app.route('/api/pay', methods=['post'])
def pay():
    try:
        utils.add_receipt(session.get('cart'))
        del session['cart']
    except:
        return jsonify({'code': 400})
    return jsonify({'code': 200})


@app.route('/receipts')
def banhang():
    kw = request.args.get('keyword')
    receipts = utils.load_receipt()
    a = []
    for c in receipts:
        u = utils.get_user_by_id(c.user_id)
        a.append(u)
    if kw:
        receipts = utils.load_receipt(kw)
        a[0] = a[int(kw)-1]
    return render_template('receipt.html',
                           receipts=receipts,
                           users=a)


@app.route('/receipt/<int:user_id>/<int:receipt_id>')
def receipt_detail(user_id, receipt_id):
    receipt = utils.get_receipt_by_id(receipt_id)
    product_id = 1
    detail = utils.get_receipt_detail_by_id(receipt_id, product_id)
    user = utils.get_user_by_id(user_id)

    return render_template('receipt-detail.html',
                           receipt=receipt,
                           user=user,
                           detail=detail)


@app.route('/api/comments', methods=['post'])
@login_required
def add_comment():
    data = request.json
    content = data.get('content')
    product_id = data.get('product_id')

    try:
        c = utils.add_comment(content=content, product_id=product_id)

        return jsonify({
            'status': 200,
            'comment': {
                "id": c.id,
                "content": c.content,
                "created_date": str(c.created_date),
                "user": {
                    'id': c.user.id,
                    'username': c.user.name,
                    'avatar': c.user.avatar
                }
            }
        })
    except:
        return {'status': 404}


@app.route('/api/products/<int:product_id>/comments')
def get_comments(product_id):
    page = request.args.get('page', 1)
    comments = utils.get_comments(product_id=product_id, page=int(page))
    results = []
    for c in comments:
        results.append({
            'id': c.id,
            'content': c.content,
            'created_date': str(c.created_date),
            'user': {
                'id': c.user.id,
                'username': c.user.username,
                'avatar': c.user.avatar
            }
        })

    return jsonify(results)


@app.route('/receipt/<int:user_id>', methods=['get', 'post'])
def pay_receipt(user_id):
    user = utils.get_user_by_id(user_id)
    receipt = utils.get_receipt_by_user_id(user_id)
    detail = utils.get_receipt_detail_by_receipt_id(user.receipts)

    return render_template('pay_receipt.html',
                           receipt=receipt,
                           user=user,
                           detail=detail,
                           stats=utils.count_cart(session.get('cart')))

#
# @app.route('/receipt/count-cart', methods=['post'])
# def count_cart():
#     data = request.json
#     cart = session.get('cart')
#
#     return jsonify(utils.count_cart(cart))


@app.route('/pay_receipt', methods=['get', 'post'])
def add_user_info():
    if request.method.__eq__('POST'):
        data = request.json
        phonenum = request.form.get('phoneNum')
        address = data.get('address')
        paymethod = data.get('paymethod')
        try:
            utils.add_payment_info(phonenum, address, paymethod)
            return redirect(url_for('index.html'))
        except Exception as ex:
            err_msg = 'he thong dang co loi' + str(ex)

    return render_template('pay_receipt.html', err_msg=err_msg)


if __name__ == "__main__":
    app.run(debug=True)
