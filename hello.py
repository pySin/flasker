from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate



# # Types of forms elements
# BooleanField, DateField, DateTimeField, DecimalField, FileField, HiddenField, MultipleField
# FieldList, FloatField, FormField, IntegerField, PasswordField, RadioField, SelectField
# SelectMultipleField, SubmitField, StringField, TextAreaField

# # Validators
# DataRequired, Email, EqualTo, InputRequired, IPAddress, Length, MacAddress, NumberRange, Optional
# Regexp, URL, UUID, AnyOf, NoneOf

# https://getbootstrap.com/ # Bootstrap templates.
# {{ url_for('user', name='Sinan') }} # Jinja2 - use 'url_for' for a route that needs a variable.

#  Create a Flask instance.
app = Flask(__name__)

# Add Database.
# Old SQLite Database.
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# New MySQL DB.
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@host(localhost)/db_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:dance@localhost/our_users'

# Initialize the database. SQLAlchemy can easily work with most Databases. We can change SQLite with
# MySQL with simple row uncommenting.
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Create a table model.
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Create a string.
    def __repr__(self):
        return '<Name %r>'


# Create a secret key for the CSRF token.
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"


# Create a form class / CSRF tokens prevents hackers.
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite color", )
    submit = SubmitField("Submit")


# Create a form class / CSRF tokens prevents hackers.
class NamerForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash('User updated successfully')
            return render_template('update.html', form=form, name_to_update=name_to_update)
        except:
            db.session.commit()
            flash('Error! There was a problem!')
            return render_template('update.html', form=form, name_to_update=name_to_update)
    else:
        return render_template('update.html', form=form, name_to_update=name_to_update)


# Route for user data input.
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data,
                         favorite_color=form.favorite_color.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        flash('User added successfully!')
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)

# Jinja tags to consider: safe, capitalize, lower, upper, title, trim, striptags
@app.route('/')
def index():
    flash("FLASH message!")  # Try a Flash message.
    first_name = "Vasilka"
    stuff = "This is <strong>bold</strong> text"
    stuff_2 = "No HTML text here"
    favorite_pizza = ['peperoni', 'mushroom', 'cheese', 41]
    return render_template('index.html',
                           first_name=first_name,
                           stuff=stuff,
                           stuff_2=stuff_2,
                           favorite_pizza=favorite_pizza)


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)

# Create custom error pages.
# Invalid URL.
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Internal server Error.
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


# Create Name Page to contain the form.
@app.route('/name', methods=['GET', 'POST'])  # We need to be able to post the form.
def name():
    name = None  # Create a name variable available on the top function level.
    form = NamerForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data  # Give the name variable another value.
        form.name.data = ''
        flash("Form submitted successfully!")
    return render_template('name.html', name=name, form=form)  # Obviously the 'name.html' page
                                            # gets re-rendered on SUBMIT.


if __name__ == '__main__':
    app.run(debug=True)
