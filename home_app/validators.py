from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def empty(value):
	if value == "":
		raise ValidationError(
			_('Invalid value: %(value)s'),
			code = "invalid",
			params={'value': 'Cannot be empty'}
			)


def isInteger(value):
	if isinstance(value, int) == False:
		raise ValidationError(
			_('Invalid value: %(value)s'),
			code = 'invalid',
			params={'value': 'Must be an integer'}
			)