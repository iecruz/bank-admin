from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from playhouse.shortcuts import model_to_dict
from core.forms import TellerLoginForm, ChangePinForm, TransactionForm
from core.wrappers import teller_auth
from core.models import Account, User, Transaction, Log, fn

from datetime import datetime, time

bp = Blueprint('teller', __name__)

@bp.route('/')
@teller_auth
def index():
    return render_template('teller/index.html')

@bp.route('/inquiry')
@teller_auth
def inquiry():
    balance = "{0:,.2f}".format(Account.get(Account.id == session['atm_auth']).balance)
    return render_template('teller/inquiry.html', balance=balance)

@bp.route('/withdraw', methods=['GET', 'POST'])
@teller_auth
def withdraw():
    if request.method == 'POST':
        account = Account.get(Account.id == session['atm_auth'])

        total_amount = (Transaction.select(fn.Sum(Transaction.amount).alias('amounts'))
            .where(
                (Transaction.account_number == account.account_number) & 
                (Transaction.created_at >= datetime.combine(datetime.today(), time.min)) & 
                (Transaction.type == 'ATM WITHDRAW')
            )
            .get()
        ).amounts or 0

        if float(total_amount) + float(request.form.get('amount')) > 25000:
            flash('You have reached the daily maximum withdraw limit')

        elif int(request.form.get('amount')) < 500:
            flash('Amount must be greater than Php 500.00')

        else:
            Account.update(balance = Account.balance - request.form.get('amount')).where(Account.id == session['atm_auth']).execute()

            Transaction.insert(
                account_number = account.account_number,
                reference_number = account.account_number,
                amount = request.form.get('amount'),
                type = 'ATM WITHDRAW'
            ).execute()
            
            return redirect(url_for('teller.inquiry'))
    return render_template('teller/withdraw.html')

@bp.route('/deposit', methods=['GET', 'POST'])
@teller_auth
def deposit():
    if request.method == 'POST':
        account = Account.get(Account.id == session['atm_auth'])

        Account.update(balance = Account.balance + request.form.get('amount')).where(Account.id == session['atm_auth']).execute()

        Transaction.insert(
            account_number = account.account_number,
            reference_number = account.account_number,
            amount = request.form.get('amount'),
            type = 'ATM DEPOSIT'
        ).execute()

        return redirect(url_for('teller.inquiry'))
    return render_template('teller/deposit.html')

@bp.route('/transfer', methods=['GET', 'POST'])
@teller_auth
def transfer():
    form = TransactionForm(request.form)
    if form.validate_on_submit():
        account = Account.get(Account.id == session['atm_auth'])

        if form.account_number.data == account.account_number:
            flash('You cannot transfer funds to your own account')

        else:
            Account.update(balance = Account.balance - form.amount.data).where(Account.id == session['atm_auth']).execute()
            Account.update(balance = Account.balance + form.amount.data).where(Account.account_number == form.account_number.data).execute()

            Transaction.insert(
                account_number = account.account_number,
                reference_number = form.account_number.data,
                amount = request.form.get('amount'),
                type = 'ATM FUND TRANSFER'
            ).execute()

            return redirect(url_for('teller.inquiry'))
    return render_template('teller/transfer.html', form=form)

@bp.route('/change_pin', methods=['GET', 'POST'])
@teller_auth
def change_pin():
    form = ChangePinForm(request.form)
    if form.validate_on_submit():
        account = Account.get(Account.id == session['atm_auth'])

        if check_password_hash(account.pin, form.current_pin.data):
            Account.update(
                pin = generate_password_hash(form.new_pin.data)
            ).where(Account.id == session['atm_auth']).execute()

            flash('PIN successfully updated')
            return redirect(url_for('teller.index'))
        else:
            flash('PIN does not match')
    return render_template('teller/change_pin.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = TellerLoginForm(request.form)
    if form.validate_on_submit():
        account = Account.get_or_none((Account.account_number == form.account_number.data) & (Account.deleted == False))

        if account and check_password_hash(account.pin, form.password.data):
            session['atm_auth'] = account.id

            return redirect(url_for('teller.index'))
        else:
            flash('Invalid Account Number and PIN')
    return render_template('teller/login.html', form=form)

@bp.route('/logout')
@teller_auth
def logout():
    session.pop('atm_auth')
    return redirect(url_for('teller.login'))