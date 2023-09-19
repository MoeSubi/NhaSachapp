from NhaSachapp import db, app
from NhaSachapp.models import Category, Product, Tag, User, UserRole, Role
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose, AdminIndexView
from flask_login import logout_user, current_user
from flask import redirect, request
from flask_admin import Admin
import utils


class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class ProductView(AuthenticatedModelView):
    can_export = True
    column_searchable_list = ['name', 'description']


class AuthenticatedBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(AuthenticatedBaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


class StatsView(AuthenticatedBaseView):
    @expose('/')
    def index(self):
        kw = request.args.get('kw')

        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        return self.render('admin/stats.html',
                           stats=utils.product_stats(kw=kw, from_date=from_date, to_date=to_date))


class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html', stats=utils.category_stats())


admin = Admin(app=app, name='Quản lí thư viện', template_mode='bootstrap4', index_view=MyAdminIndex())
admin.add_view(AuthenticatedModelView(Category, db.session, name="Thể loại"))
admin.add_view(ProductView(Product, db.session, name="Sách"))
admin.add_view(AuthenticatedModelView(Tag, db.session, name="Tag"))
admin.add_view(AuthenticatedModelView(User, db.session, name="Người dùng"))
admin.add_view(StatsView(name='Thống kê báo cáo'))
admin.add_view(AuthenticatedModelView(Role,db.session,name="Quy tắc"))
admin.add_view(LogoutView(name='Đăng xuất'))
