from wtforms import form, fields, validators
from werkzeug.security import check_password_hash
from admin_models import db, User

# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    email = fields.StringField(validators=[validators.required()])
    senha = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Email invalido')

        if not check_password_hash(user.password, self.senha.data):
            raise validators.ValidationError('Senha invalida')

    def get_user(self):
        return db.session.query(User).filter_by(email=self.email.data).first()