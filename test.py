from flask import Flask
from werkzeug.datastructures import MultiDict
from app.forms import ProfileForm


def _make_test_app():
	app = Flask(__name__)
	app.config['SECRET_KEY'] = 'test-secret'
	# Disable CSRF for form testing convenience
	app.config['WTF_CSRF_ENABLED'] = False
	return app


def test_email_validation_rejects_invalid():
	"""Submitting an invalid email should fail form validation."""
	app = _make_test_app()
	with app.test_request_context(method='POST'):
		formdata = MultiDict({
			'username': 'tester',
			'full_name': 'Test User',
			'email': 'not-an-email',
			'age': '30',
			'bio': 'hello',
			'submit': 'Save'
		})
		form = ProfileForm(formdata=formdata)
		assert not form.validate()
		assert 'email' in form.errors


def test_email_validation_accepts_valid():
	"""A well-formed email should pass validation."""
	app = _make_test_app()
	with app.test_request_context(method='POST'):
		formdata = MultiDict({
			'username': 'tester2',
			'full_name': 'Valid User',
			'email': 'valid@example.com',
			'age': '25',
			'bio': 'hi',
			'submit': 'Save'
		})
		form = ProfileForm(formdata=formdata)
		assert form.validate()
