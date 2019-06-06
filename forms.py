from flask_wtf import Form
from wtforms import StringField, TextAreaField, PasswordField, DateField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User

class RegistrationForm(Form):
	username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField("Email", validators=[DataRequired(), Email()])
	password = PasswordField("Password", validators=[DataRequired()])
	confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])

	def validate_username(self, username):
		user = User.select().where(User.username == username.data)
		if user:
			raise ValidationError("That username is taken. Choose a different one.")

	def validate_email(self, email):
		user = User.select().where(User.email == email.data)
		if user:
			raise ValidationError("That email is taken. Choose a different one.")


class LoginForm(Form):
	email = StringField("Email", validators=[DataRequired(), Email()])
	password = PasswordField("Password", validators=[DataRequired()])
	remember_me = BooleanField("Remember Me")


class Journal_Entry(Form):
	title = StringField("Title", validators=[DataRequired()])
	date = DateField("Date", validators=[DataRequired()])
	time_spent = IntegerField("Time Spent", validators=[DataRequired()])
	what_you_learned = TextAreaField("What You Learned", validators=[DataRequired()])
	resources_to_remember = TextAreaField("Resources to Remember", validators=[DataRequired()])
	tags = StringField("Tags", validators=[DataRequired()])