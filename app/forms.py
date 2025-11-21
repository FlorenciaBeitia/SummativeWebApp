"""
Flask-WTF form definitions and validation.
- Using FlaskForm gives us CSRF protection and built-in validators.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=30)])
    full_name = StringField('Full name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    age = IntegerField('Age', validators=[DataRequired(message='Age is required'), NumberRange(min=1, max=120, message='Age must be at least 1')])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    submit = SubmitField('Save')

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')

