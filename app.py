import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create Flask application
app = Flask(__name__)

# Create dummy secret key so we can use sessions
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

from admin_views import *


def build_ezztracker_db():
    """
    Populate a small db with some example entries.
    """

    import string
    import random
    from admin_models import db, Company, Role, User

    db.drop_all()
    db.create_all()

    with app.app_context():

        company = Company(id=1, company_name=app.config['COMPANY_NAME'])
        db.session.add(company)

        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        user = User(
            login='admin',
            first_name='Admin',
            email='admin@ebizz.com.br',
            password=generate_password_hash('admin'),
            company_id=1,
            roles=[user_role, super_user_role]
        )

        db.session.add(user)

        first_names = [
            'Harry', 'Amelia', 'Oliver', 'Jack', 'Isabella', 'Charlie', 'Sophie', 'Mia',
            'Jacob', 'Thomas', 'Emily', 'Lily', 'Ava', 'Isla', 'Alfie', 'Olivia', 'Jessica',
            'Riley', 'William', 'James', 'Geoffrey', 'Lisa', 'Benjamin', 'Stacey', 'Lucy'
        ]
        last_names = [
            'Brown', 'Smith', 'Patel', 'Jones', 'Williams', 'Johnson', 'Taylor', 'Thomas',
            'Roberts', 'Khan', 'Lewis', 'Jackson', 'Clarke', 'James', 'Phillips', 'Wilson',
            'Ali', 'Mason', 'Mitchell', 'Rose', 'Davis', 'Davies', 'Rodriguez', 'Cox', 'Alexander'
        ]

        for i in range(len(first_names)):
            tmp_email = first_names[i].lower() + "." + last_names[i].lower() + "@example.com"
            tmp_pass = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(10))
            user = User(
                first_name=first_names[i],
                last_name=last_names[i],
                email=tmp_email,
                password=generate_password_hash(tmp_pass),
                roles=[user_role, ]
            )
            db.session.add(user)
        db.session.commit()
    return

if __name__ == '__main__':

    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])

    print database_path
    if not os.path.exists(database_path):
        build_ezztracker_db()

    # Start app
    app.run(debug=True)