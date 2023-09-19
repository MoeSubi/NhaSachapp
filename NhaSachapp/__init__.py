from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = 'Rawrfafgawgawgfawfgawf'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:12345678@localhost/nhasachapp?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['PAGE_SIZE'] = 8
app.config['COMMENT_SIZE'] = 5
db = SQLAlchemy(app=app)
login = LoginManager(app=app)

cloudinary.config(
    cloud_name='dxnka0r7n',
    api_key='583137964568386',
    api_secret='gjfp2YfQZe99nePkAznAsSEWiNE'
)
