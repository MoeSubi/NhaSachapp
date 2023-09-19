from NhaSachapp import db
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Enum
from datetime import datetime
from sqlalchemy.orm import relationship, backref
from enum import Enum as UserEnum
from flask_login import UserMixin


class UserRole(UserEnum):
    ADMIN = 1
    USER = 2


class Category(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    products = relationship('Product', backref='category', lazy=True)
    product_tag = db.Table('product_tag',
                           Column('product_id', Integer, ForeignKey('product.id'), primary_key=True),
                           Column('tag_id', Integer, ForeignKey('tag.id'), primary_key=True))

    def __str__(self):
        return self.name


class Product(db.Model):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, default=0)
    pages = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    description = Column(String(100))
    images = Column(String(100))
    create_date = Column(DateTime, default=datetime.now())
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    tags = relationship('Tag', secondary='product_tag', lazy='subquery',
                        backref=backref('products', lazy=True))
    receipt_details = relationship('ReceiptDetail', backref='product', lazy=True)
    comments = relationship('Comment', backref='product', lazy=False)


class Tag(db.Model):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(50), nullable=False)
    email = Column(String(50))
    active = Column(Boolean, default=True)
    join_date = Column(DateTime, default=datetime.now())
    avatar = Column(String(100))
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    receipts = relationship('Receipt', backref='user', lazy=True)
    comments = relationship('Comment', backref='user', lazy=True)
    # payment_info = relationship('PaymentInfo', backref('user'), lazy=True)

    def __str__(self):
        return self.name


class Comment(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(255), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    uer_id = Column(Integer, ForeignKey(User.id), nullable=False)
    created_date = Column(DateTime, default=datetime.now())

    def __str__(self):
        return self.content


class Receipt(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    details = relationship('ReceiptDetail', backref='receipt', lazy=True)
    # payment_info = relationship('PaymentInfo', backref('receipt'), lazy=True)


class ReceiptDetail(db.Model):
    receipt_id = Column(Integer, ForeignKey(Receipt.id), nullable=False, primary_key=True)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False, primary_key=True)
    quantity = Column(Integer, default=0)
    unit_price = Column(Float, default=0)


class Role(db.Model):
    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(255), nullable=False)
    role_info = Column(String(255), nullable=False)


class PaymentInfo(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    # receipt_id = Column(Integer, ForeignKey(Receipt.id), nullable=False, primary_key=True)
    phoneNum = Column(String(20), nullable=False)
    address = Column(String(50), nullable=False)
    payMethod = Column(String(20), nullable=False)


if __name__ == '__main__':
     db.create_all()
