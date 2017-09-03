from app import db
from flask_security import UserMixin, RoleMixin

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey("user.id")),
    db.Column('role_id', db.Integer(), db.ForeignKey("role.id"))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), unique=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(100))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    telephone = db.Column(db.String(50), nullable=True)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    company = db.relationship('Company', backref=db.backref('user_company'))

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __unicode__(self):
        return self.email

    def __str__(self):
        return self.email


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(50))
    description = db.Column(db.Text, nullable=True)

    def __str__(self):
        return self.company_name


class Os(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    initials = db.Column(db.String(50))
    version = db.Column(db.String(50))

    def __str__(self):
        return self.name + " " + self.version


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    initials = db.Column(db.String(50))
    version = db.Column(db.String(50))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    os_id = db.Column(db.Integer, db.ForeignKey('os.id'))
    company = db.relationship('Company', backref=db.backref('products_company'))
    os = db.relationship('Os', backref=db.backref('products_os'))

    def __str__(self):
        return self.initials + " " + self.version


class Priority(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __str__(self):
        return self.name


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __str__(self):
        return self.name


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    priority_id = db.Column(db.Integer, db.ForeignKey('priority.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    description = db.Column(db.Text)
    priority = db.relationship('Priority', backref=db.backref('track_priority'))
    product = db.relationship('Products', backref=db.backref('track_product'))
    requester = db.relationship('User', backref=db.backref('track_requester'))
    status = db.relationship('Status', backref=db.backref('track_status'))

    def __str__(self):
        return "#" + str(self.id) + " - " + self.title


class TrackHandler(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    handler_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tracker_id = db.Column(db.Integer, db.ForeignKey('track.id'))
    handler = db.relationship('User', backref=db.backref('trackhandler_handler'))
    tracker = db.relationship('Track', backref=db.backref('trackhandler_tracker'))
    handle_at = db.Column(db.DateTime())