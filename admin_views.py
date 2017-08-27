from flask_admin.contrib import sqla
from wtforms import validators, PasswordField


class UserView(sqla.ModelView):
    form_columns = ['first_name', 'last_name', 'company', 'email', 'telephone', 'password', 'active', 'roles', 'confirmed_at']
    column_labels = dict(first_name='Primeiro nome', last_name='Sobrenome', company='Empresa', telephone='Telefone',
                         password='Senha', active='Ativo', roles='Funcao', confirmed_at='Confirmado')
    column_exclude_list = ['password', ]
    column_descriptions = dict(first_name="Primeiro nome")
    # Define as colunas para busca
    column_searchable_list = ('first_name', 'email')
    # Define a ordem que sao mostradas as linhas: False ordem crescente, True ordem descendente
    column_default_sort = ('first_name', False)
    column_filters = ('first_name', 'email')
    create_modal = True
    edit_modal = True

    form_args = {
        'first_name': {
            'validators': [validators.DataRequired(), validators.Length(min=5, max=50)]
        },
        'password': {
            'validators': [validators.DataRequired(), validators.Length(min=8, max=16)]
        }


    }

    form_extra_fields = {
        'password': PasswordField('Senha')
    }


class TrackView(sqla.ModelView):
    form_columns = ['title', 'priority', 'product', 'requester', 'status', 'description']
    column_list = ('id', 'title', 'priority', 'requester', 'status')
    create_modal = True
    edit_modal = True


class CompanyView(sqla.ModelView):
    form_columns = ['company_name', 'description']
    create_modal = True
    edit_modal = True


class OsView(sqla.ModelView):
    form_columns = ['name', 'initials', 'version']
    create_modal = True
    edit_modal = True

    # Deopis que acontece uma alteracao ou uma insercao fazer uma acao, como por exemplo, enviar um email
    def after_model_change(self, form, model, is_created):
        if is_created:
            print "O model foi criado: " + str(model.id) + " " + model.name
        else:
            print "o model foi alterado"


class StatusView(sqla.ModelView):
    form_columns = ['name', ]
    create_modal = True
    edit_modal = True


class PriorityView(sqla.ModelView):
    form_columns = ['name', ]
    create_modal = True
    edit_modal = True


class ProductsView(sqla.ModelView):
    form_columns = ['name', 'initials', 'version', 'company', 'os']


class TrackHandlerView(sqla.ModelView):
    form_columns = ['handler', 'tracker', 'handle_at']
