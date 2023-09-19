from flask import request

from NhaSachapp.models import User, PaymentInfo
import hashlib
from NhaSachapp.models import Category, Product, Receipt, ReceiptDetail, Comment
from NhaSachapp import app, db
from flask_login import current_user
from sqlalchemy import func


def get_user_by_id(user_id):
    return User.query.get(user_id)


def check_login(username, password):
    if username and password:
        password = hashlib.md5(password.strip().encode('utf-8')).hexdigest()

        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password)).first()

    return None


def load_categories():
    return Category.query.all()


def load_products(cate_id=None, kw=None, from_price=None, to_price=None, page=1):
    products = Product.query.filter(Product.active.__eq__(True))

    if cate_id:
        products = products.filter(Product.category_id.__eq__(cate_id))

    if kw:
        products = products.filter(Product.name.contains(kw))

    if from_price:
        products = products.filter(Product.price.__ge__(from_price))
    if to_price:
        products = products.filter(Product.price.__le__(to_price))

    page_size = app.config['PAGE_SIZE']
    start = (page-1)*page_size
    end = start + page_size

    return products.slice(start, end).all()


def get_product_by_id(product_id):
    return Product.query.get(product_id)


def get_receipt_by_id(receipt_id):
    return Receipt.query.get(receipt_id)


def get_receipt_detail_by_id(receipt_id, product_id):
    return ReceiptDetail.query.filter(ReceiptDetail.receipt_id.__eq__(receipt_id),
                                      ReceiptDetail.product_id.__eq__(product_id))


def get_receipt_by_user_id(user_id):
    return Receipt.query.filter(Receipt.user_id.__eq__(user_id))


def get_receipt_detail_by_receipt_id(receipt):
    return ReceiptDetail.query.filter(ReceiptDetail.receipt_id.__eq__(receipt))


def count_products():
    return Product.query.filter(Product.active.__eq__(True)).count()


def add_user(name, username, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(name=name, username=username,
                password=password,
                email=kwargs.get('email'),
                avatar=kwargs.get('avatar'))

    db.session.add(user)
    db.session.commit()


def check_login(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()


def count_cart(cart):
    total_quantity, total_amount = 0, 0
    if cart:
        for c in cart.values():
            total_quantity += c['quantity']
            total_amount += c['quantity'] * c['price']
    return {
        'total_quantity': total_quantity,
        'total_amount': total_amount
    }


def add_receipt(cart, phonenum, address, paymethod):
    if cart:
        receipt = Receipt(user=current_user, phoneNum=phonenum, address=address, payMethod=paymethod)
        db.session.add(receipt)
        for c in cart.values():
            d = ReceiptDetail(receipt=receipt,
                              product_id=c['id'],
                              quantity=c['quantity'],
                              unit_price=c['price'])
        db.session.add(d)
    db.session.commit()


def category_stats():
    return db.session.query(Category.id, Category.name, func.count(Product.id))\
                            .join(Product, Category.id.__eq__(Product.category_id), isouter=True)\
                            .group_by(Category.id, Category.name).all()


def product_stats(kw=None, from_date=None, to_date=None):
    p = db.session.query(Product.id, Product.name, func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price)) \
        .join(ReceiptDetail, ReceiptDetail.product_id.__eq__(Product.id), isouter=True)\
        .join(Receipt, Receipt.id.__eq__(ReceiptDetail.receipt_id)) \
        .group_by(Product.id, Product.name)
    if kw:
        p = p.filter(Product.name.contains(kw))
    if from_date:
        p = p.filter(Receipt.created_date.__ge__(from_date))
    if to_date:
        p = p.filter(Receipt.created_date.__le__(to_date))
    return p.all()


def add_comment(content, product_id):
    c = Comment(content=content, product_id=product_id, user=current_user)

    db.session.add(c)
    db.session.commit()

    return c


def get_comments(product_id, page=1):
    page_size = app.config['COMMENT_SIZE']
    start = (page - 1) * page_size
    end = start + page_size

    return Comment.query.filter(Comment.product_id.__eq__(product_id))\
        .order_by(-Comment.id).slice(start, end).all()


def count_comments(product_id):
    return Comment.query.filter(Comment.product_id.__eq__(product_id)).count()


def load_receipt(kw=None):
    if kw:
        receipts = Receipt.query.filter(Receipt.id.__eq__(kw))
        return receipts
    else:

        return Receipt.query.all()


def add_payment_info(phone, address, pay_method):
    info = PaymentInfo(phoneNum=phone, address=address, payMethod=pay_method)

    db.session.add(info)
    db.session.commit()
