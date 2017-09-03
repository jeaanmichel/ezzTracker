from app import app
from flask import url_for, redirect, render_template, request
from admin_models import db, User, Company, Track, TrackHandler, Priority, Products, Os, Status
from admin_forms import LoginForm
from flask_admin.contrib import sqla
from flask_admin import helpers, expose
import flask_admin as admin
from wtforms import validators, PasswordField
import flask_login as login
from werkzeug.security import generate_password_hash


class UserView(sqla.ModelView):
    def is_accessible(self):

        if not login.current_user.is_active or not login.current_user.is_authenticated:
            return False

        if login.current_user.has_role('superuser'):
            return True

        return False

    form_columns = ['first_name', 'last_name', 'company', 'email', 'telephone', 'password', 'active',
                    'roles']
    column_labels = dict(first_name='Primeiro nome', last_name='Sobrenome', company='Empresa', telephone='Telefone',
                         password='Senha', active='Ativo', roles='Funcao', confirmed_at='Confirmado')
    column_exclude_list = ['password', ]
    #column_descriptions = dict(first_name="Primeiro nome")
    # Define as colunas para busca
    column_searchable_list = ('first_name', 'email')
    # Define a ordem que sao mostradas as linhas: False ordem crescente, True ordem descendente
    column_default_sort = ('first_name', False)
    column_filters = ('first_name', 'email')
    create_modal = False
    edit_modal = True

    form_args = {
        'first_name': {
            'validators': [validators.DataRequired(), validators.Length(min=5, max=50)]},
        'password': {
            'validators': [validators.DataRequired(), validators.Length(min=8, max=16)]},
        'last_name': {
            'validators': [validators.DataRequired(), validators.Length(min=5, max=50)]},
        'company': {
            'validators': [validators.DataRequired()]},
        'email': {
            'validators': [validators.DataRequired(), validators.Email(), validators.Length(min=5, max=50)]
        }
    }

    form_extra_fields = {
        'password': PasswordField('Senha')
    }

    def on_model_change(self, form, model, is_created):
        if form.password.data is not None and form.password.data != '':
            model.password = generate_password_hash(form.password.data)

class TrackView(sqla.ModelView):
    form_columns = ['title', 'priority', 'product', 'requester', 'status', 'description']
    column_list = ('id', 'title', 'priority', 'requester', 'status')
    column_filters = ('title', 'priority', 'requester', 'status')
    create_modal = False
    edit_modal = True

    form_args = {
        'title': {
            'validators': [validators.DataRequired(), validators.Length(min=5)]
        },
        'priority': {
            'validators': [validators.DataRequired()]
        },
        'product': {
            'validators': [validators.DataRequired()]
        },
        'requester': {
            'validators': [validators.DataRequired()]
        },
        'status': {
            'validators': [validators.DataRequired()]
        }
    }

    def is_accessible(self):
        if not login.current_user.is_active or not login.current_user.is_authenticated:
            return False

        if login.current_user.has_role('superuser'):
            return True

        return False


class CompanyView(sqla.ModelView):
    form_columns = ['company_name', 'description']
    create_modal = False
    edit_modal = True

    form_args = {
        'company_name':{
            'validators': [validators.DataRequired()]
        }
    }

    def is_accessible(self):
        if not login.current_user.is_active or not login.current_user.is_authenticated:
            return False

        if login.current_user.has_role('superuser'):
            return True

        return False


class OsView(sqla.ModelView):
    form_columns = ['name', 'initials', 'version']
    create_modal = False
    edit_modal = True

    form_args = {
        'name': {
            'validators': [validators.DataRequired()]
        }
    }

    def is_accessible(self):
        if not login.current_user.is_active or not login.current_user.is_authenticated:
            return False

        if login.current_user.has_role('superuser'):
            return True

        return False

    # Deopis que acontece uma alteracao ou uma insercao fazer uma acao, como por exemplo, enviar um email
    def after_model_change(self, form, model, is_created):
        if is_created:
            print "O model foi criado: " + str(model.id) + " " + model.name
        else:
            print "o model foi alterado"


class StatusView(sqla.ModelView):
    form_columns = ['name', ]
    create_modal = False
    edit_modal = True

    form_args = {
        'name': {
            'validators': [validators.DataRequired()]
        }
    }

    def is_accessible(self):
        if not login.current_user.is_active or not login.current_user.is_authenticated:
            return False

        if login.current_user.has_role('superuser'):
            return True

        return False


class PriorityView(sqla.ModelView):
    form_columns = ['name', ]
    create_modal = False
    edit_modal = True

    form_args = {
        'name': {
            'validators': [validators.DataRequired()]
        }
    }

    def is_accessible(self):
        if not login.current_user.is_active or not login.current_user.is_authenticated:
            return False

        if login.current_user.has_role('superuser'):
            return True

        return False


class ProductsView(sqla.ModelView):
    form_columns = ['name', 'initials', 'version', 'company', 'os']
    create_modal = False
    edit_modal = True

    form_args = {
        'name': {
            'validators': [validators.DataRequired()]
        },
        'company': {
            'validators': [validators.DataRequired()]
        },
        'os': {
            'validators': [validators.DataRequired()]
        }
    }

    def is_accessible(self):
        if not login.current_user.is_active or not login.current_user.is_authenticated:
            return False

        if login.current_user.has_role('superuser'):
            return True

        return False


class TrackHandlerView(sqla.ModelView):
    form_columns = ['handler', 'tracker']
    create_modal = False
    edit_modal = True

    form_args = {
        'handler': {
            'validators': [validators.DataRequired()]
        },
        'tracker': {
            'validators': [validators.DataRequired()]
        }
    }

    def is_accessible(self):
        if not login.current_user.is_active or not login.current_user.is_authenticated:
            return False

        if login.current_user.has_role('superuser'):
            return True

        return False


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()

            if user:
                login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        link = ''
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


# Flask views
@app.route('/')
def index():
    return render_template('index.html')


@app.errorhandler(403)
def page_not_found(e):
    return '<h1>HA HA! Vc nao tem autorizacao pra acessar esta pagina</h1>', 403


# Initialize flask-login
init_login()

# Create admin
admin = admin.Admin(app, 'ezzTracker Admin', index_view=MyAdminIndexView(), base_template='my_master.html')

admin.add_view(TrackView(Track, db.session))
admin.add_view(TrackHandlerView(TrackHandler, db.session))
admin.add_view(UserView(User, db.session))
admin.add_view(CompanyView(Company, db.session))
admin.add_view(ProductsView(Products, db.session))
admin.add_view(OsView(Os, db.session))
admin.add_view(StatusView(Status, db.session))
admin.add_view(PriorityView(Priority, db.session))

