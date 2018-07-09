from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash
from core.models import User
from core.forms import CreateUserForm, UpdateUserForm, ChangePasswordForm
from core.wrappers import authenticated

from datetime import datetime

bp = Blueprint('user', __name__)

@bp.route('/')
@authenticated
def index():
    users = User.select().execute()
    return render_template('user/index.html', users=users)

@bp.route('/view/<int:id>')
@authenticated
def view(id):
    user = User.get(User.id == id)
    return render_template('user/view.html', user=user)

@bp.route('/create', methods=['GET', 'POST'])
@authenticated
def create():
    form = CreateUserForm(request.form)
    if form.validate_on_submit():
        User.insert(
            first_name = form.first_name.data,
            middle_name = form.middle_name.data,
            last_name = form.last_name.data,
            email_address = form.email_address.data,
            phone_number = form.phone_number.data,
            address = form.address.data,
            birth_date = form.birth_date.data,
            type = form.type.data,
            password = generate_password_hash(form.password.data),
        ).execute()
        flash('User successfully registered')
        return redirect(url_for('user.index'))
    return render_template('user/create.html', form=form)

@bp.route('/update/<int:id>', methods=['GET', 'POST'])
@authenticated
def update(id):
    form = UpdateUserForm(request.form)
    user = User.get(User.id == id)
    if form.validate_on_submit():
        User.update(
            first_name = form.first_name.data,
            middle_name = form.middle_name.data,
            last_name = form.last_name.data,
            email_address = form.email_address.data,
            phone_number = form.phone_number.data,
            address = form.address.data,
            birth_date = form.birth_date.data,
            type = form.type.data,
            updated_at=datetime.now()
        ).where(User.id == id).execute()
        flash('User successfully updated')
        return redirect(url_for('user.index'))
    return render_template('user/update.html', form=form, user=user)

@bp.route('/change_password', methods=['GET', 'POST'])
@authenticated
def change_password():
    form = ChangePasswordForm(request.form)
    if form.validate_on_submit():
        User.update(
            password = generate_password_hash(form.new_password.data),
        ).where(User.id == form.user_id.data).execute()
        flash('Password successfully changed')
        return redirect(url_for('user.index'))
    return render_template('user/change_password.html', form=form)

@bp.route('/deactivate/<int:id>', methods=['POST'])
@authenticated
def deactivate(id):
    User.update(
        deleted=True,
        updated_at=datetime.now()
    ).where(User.id == id).execute()
    return redirect(url_for('user.index'))

@bp.route('/activate/<int:id>', methods=['POST'])
@authenticated
def activate(id):
    User.update(
        deleted=False,
        updated_at=datetime.now()
    ).where(User.id == id).execute()
    return redirect(url_for('user.index'))