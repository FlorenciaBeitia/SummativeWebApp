"""
Routes for the profiles app.
- List, register, view and update users as well as allows users registered to be deleted.
"""
from flask import Blueprint, current_app, render_template, redirect, url_for, request, flash
from .db import get_db_connection, delete_user
from .forms import ProfileForm, DeleteForm
import sqlite3

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Show a list of Registered users."""
    db = get_db_connection(current_app.config['DATABASE'])
    users = db.execute('SELECT id, username, full_name, email FROM users ORDER BY id DESC').fetchall()
    db.close()
    return render_template('index.html', users=users)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Create a new user from form data."""
    form = ProfileForm()
    if form.validate_on_submit():
        db = get_db_connection(current_app.config['DATABASE'])
        try:
            db.execute(
                'INSERT INTO users (username, full_name, email, age, bio) VALUES (?, ?, ?, ?, ?)',
                (form.username.data.strip(), form.full_name.data.strip(),
                 form.email.data.strip(), int(form.age.data), (form.bio.data or '').strip())
            )
            db.commit()
            flash('User registered successfully.', 'success')
            return redirect(url_for('main.index'))
        except sqlite3.IntegrityError:
            # Handle unique constraint violations for username/email
            flash('Error: username or email already exists.', 'error')
        finally:
            db.close()
    return render_template('register.html', form=form)

@bp.route('/profile/<int:user_id>')
def profile(user_id):
    """Display a single user's profile dynamically."""
    db = get_db_connection(current_app.config['DATABASE'])
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    db.close()
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('main.index'))
    # Provide a small delete form for CSRF protection when deleting
    delete_form = DeleteForm()
    return render_template('profile.html', user=user, delete_form=delete_form)


@bp.route('/delete/<int:user_id>', methods=['POST'])
def delete(user_id):
    """Delete a user after confirmation (POST only)."""
    #Delete a user after confirmation
    form = DeleteForm()
    if not form.validate_on_submit():
        flash('Invalid request or missing CSRF token.', 'error')
        return redirect(url_for('main.profile', user_id=user_id))

    db = get_db_connection(current_app.config['DATABASE'])
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    db.close()
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('main.index'))

    ok = delete_user(current_app.config['DATABASE'], user_id)
    if ok:
        flash('User deleted.', 'success')
    else:
        flash('Could not delete user.', 'error')
    return redirect(url_for('main.index'))

@bp.route('/update/<int:user_id>', methods=['GET', 'POST'])
def update(user_id):
    """Preload user data into the form for update and save changes."""
    db = get_db_connection(current_app.config['DATABASE'])
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        db.close()
        flash('User not found', 'error')
        return redirect(url_for('main.index'))

    form = ProfileForm()
    if request.method == 'GET':
        # Preload current values into the form so user can edit them
        form.username.data = user['username']
        form.full_name.data = user['full_name']
        form.email.data = user['email']
        form.age.data = user['age'] if user['age'] is not None else None
        form.bio.data = user['bio']
    elif form.validate_on_submit():
        try:
            db.execute(
                'UPDATE users SET username = ?, full_name = ?, email = ?, age = ?, bio = ? WHERE id = ?',
                (form.username.data.strip(), form.full_name.data.strip(),
                 form.email.data.strip(), int(form.age.data), (form.bio.data or '').strip(), user_id)
            )
            db.commit()
            flash('User updated successfully.', 'success')
            db.close()
            return redirect(url_for('main.profile', user_id=user_id))
        except sqlite3.IntegrityError:
            flash('Error updating user: username or email conflict.', 'error')
    db.close()
    return render_template('update.html', form=form, user=user)
