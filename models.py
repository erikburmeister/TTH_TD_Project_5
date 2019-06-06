import datetime
from flask_bcrypt import generate_password_hash
from flask_login import UserMixin

from peewee import *

DATABASE = SqliteDatabase("my_journal.db")

class User(UserMixin, Model):
	id = AutoField()
	username = CharField(unique=True, null=False, max_length=20)
	email = CharField(unique=True, null=False, max_length=50)
	password = CharField(max_length=100, null=False)
	joined_at = DateTimeField(default=datetime.datetime.utcnow)
	is_admin = BooleanField(default=False)

	class Meta:
		database = DATABASE
		order_by = ("-Joined_at",)

	def __repr__(self):
		return "User('{}', '{}')".format(self.username, self.email)

	@classmethod
	def create_user(cls, username, email, password, admin=False):
		try:
			with DATABASE.transaction():
				cls.create(
					username=username,
					email=email,
					password=generate_password_hash(password),
					is_admin=admin)

		except IntegrityError:
			raise ValueError("User already exists")


class Journal(Model):
	title = CharField(max_length=100)
	date = DateField(formats=['%Y-%m-%d'])
	time_spent = IntegerField(default=0)
	what_you_learned = TextField()
	resources_to_remember = TextField()
	slug = TextField()
	user_id = ForeignKeyField(model=User, backref='user')
	tags = CharField()

	class Meta:
		database = DATABASE


def initialize():
	DATABASE.connect()
	DATABASE.create_tables([User, Journal], safe=True)
	DATABASE.close()