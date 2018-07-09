from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms.fields import StringField, PasswordField, IntegerField, DecimalField, SelectField
from wtforms.fields.html5 import TelField, EmailField, DateField
from wtforms.validators import Required, Email, Regexp, EqualTo, Length, NumberRange, ValidationError
from core.models import User, Account

def validate_account_number(form, field):
    if not Account.get_or_none((Account.account_number == field.data) & (Account.deleted == False)):
        raise ValidationError('Account is inactivate or does not exists')

def validate_time_deposit(form, field):
    if not Account.get_or_none((Account.account_number == field.data) & (Account.time_deposit == 0)):
        raise ValidationError('Account is currently holding an existing time deposit')

class TellerLoginForm(FlaskForm):
    account_number = StringField('Account Number', [Required(), validate_account_number])
    password = PasswordField('PIN', [Required()])

class ChangePinForm(FlaskForm):
    current_pin = PasswordField('Current PIN', [Required(), Regexp('[0-9]{4,6}', message='PIN must be 4 digits')])
    new_pin = PasswordField('New PIN', [Required(), EqualTo('confirm_pin', message='PIN must match'), Regexp('[0-9]{4,6}', message='PIN must be 4 digits')])
    confirm_pin = PasswordField('Confirm PIN', [Required(), Regexp('[0-9]{4,6}', message='PIN must be 4 digits')])
    
class LoginForm(FlaskForm):
    email_address = EmailField('Email Address', [Required(), Email()])

    def validate_email_address(form, field):
        user = User.get_or_none(User.email_address == field.data)
        if not user:
            raise ValidationError('Invalid email address and password')
        elif user.type > 3:
            raise ValidationError('User does not have administration or operator privileges')
        elif not check_password_hash(user.password, form.password.data):
            raise ValidationError('Invalid email address and password')

    password = PasswordField('Password', [Required()])

class CreateUserForm(FlaskForm):
    first_name = StringField('First Name', [Required()])
    middle_name = StringField('Middle Name', [Required()])
    last_name = StringField('Last Name', [Required()])
    email_address = EmailField('Email Address', [Email(), Required()])
    phone_number = TelField('Phone Number', [Required(), Length(7,11), Regexp('[0-9]+')])
    address = StringField('Address', [Required()])
    birth_date = DateField('Birth Date', [Required()])
    password = PasswordField('Password', [Required(), Length(8), EqualTo('confirm_password', message='Password must match')])
    confirm_password = PasswordField('Confirm Password', [Required(), Length(8)])
    type = SelectField('Type', [Required()], choices=[
        (9, 'Regular Customer'),
        (3, 'Operator'),
        (1, 'Administrator')
    ], coerce=int)

class ChangePasswordForm(FlaskForm):
    user_id = IntegerField('User ID', [Required()])
    def validate_user_id(form, field):
        if not User.get_or_none(User.id == field.data):
            raise ValidationError('User does not exist')

    current_password = PasswordField('Current Password', [Required(), Length(8)])
    def validate_current_password(form, field):
        user = User.get_or_none(User.id == form.user_id.data)
        if not user or not check_password_hash(user.password, field.data):
            raise ValidationError('Password does not match your current password')

    new_password = PasswordField('New Password', [Required(), Length(8), EqualTo('confirm_password', message='Password must match')])
    confirm_password = PasswordField('Confirm New Password', [Required(), Length(8)])

class UpdateUserForm(FlaskForm):
    first_name = StringField('First Name', [Required()])
    middle_name = StringField('Middle Name', [Required()])
    last_name = StringField('Last Name', [Required()])
    email_address = EmailField('Email Address', [Email(), Required()])
    phone_number = TelField('Phone Number', [Required(), Length(7,11), Regexp('[0-9]+')])
    address = StringField('Address', [Required()])
    birth_date = DateField('Birth Date', [Required()])
    type = SelectField('Type', [Required()], choices=[
        (9, 'Regular Customer'),
        (3, 'Operator'),
        (1, 'Administrator')
    ], coerce=int)

class CreateAccountForm(FlaskForm):
    user_id = IntegerField('User ID', [Required()])
    def validate_user_id(form, field):
        if not User.get_or_none((User.id == field.data) & (User.type == 9)):
            raise ValidationError('Customer does not exists')
            
    pin = IntegerField('PIN', [Required(), NumberRange(1000,9999)])
    balance = DecimalField('Initial Deposit', [Required(), NumberRange(1000)], places=2)

class TransactionForm(FlaskForm):
    account_number = IntegerField('Account Number', [Required(), validate_account_number])
    amount = DecimalField('Amount', [Required(), NumberRange(500)], places=2)

class TimeDepositForm(FlaskForm):
    account_number = IntegerField('Account Number', [Required(), validate_account_number, validate_time_deposit])
    duration = SelectField('Duration', [Required()], coerce=int)
    amount = DecimalField('Amount', [Required(), NumberRange(500)], places=2)

class TransferForm(FlaskForm):
    sender_account_number = IntegerField('Sender Account Number', [Required(), validate_account_number])
    receiver_account_number = IntegerField('Receiver Account Number', [Required(), validate_account_number])
    amount = DecimalField('Amount', [Required(), NumberRange(500)], places=2)

class InquiryForm(FlaskForm):
    account_number = IntegerField('Account Number', [Required(), validate_account_number])