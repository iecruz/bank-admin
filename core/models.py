from peewee import *
from playhouse.db_url import connect

import os
from datetime import datetime, date

db = connect(os.getenv('DATABASE_URL', 'postgres://postgres:postgres@localhost:5432/bank'));

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    id = PrimaryKeyField(index=True)
    first_name = CharField()
    middle_name = CharField()
    last_name = CharField()
    email_address = CharField(unique=True)
    phone_number = CharField()
    address = CharField()
    birth_date = DateField()
    password = CharField()
    type = IntegerField(default=9)
    deleted = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(default=datetime.now())

    class Meta:
        table_name = 'users'

class Account(BaseModel):
    id = PrimaryKeyField(index=True)
    user_id = ForeignKeyField(User)
    account_number = CharField(index=True, unique=True)
    pin = CharField()
    checking_balance = DecimalField(decimal_places=2)
    savings_balance = DecimalField(decimal_places=2)
    deleted = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(default=datetime.now())

    class Meta:
        table_name = 'accounts'

class Transaction(BaseModel):
    id = PrimaryKeyField(index=True)
    account_number = CharField()
    amount = DecimalField(decimal_places=2)
    type = CharField()
    reference_number = CharField()
    created_at = DateTimeField(default=datetime.now())

    class Meta:
        table_name = 'transactions'

def connect_db():
    db.connect(reuse_if_open=True)
    db.create_tables([User, Account, Transaction])

def close_db():
    if not db.is_closed():
        db.close()