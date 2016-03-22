import socket
from django.core.exceptions import ValidationError
from django.forms import CharField
from django.forms.widgets import Input


class Html5EmailField(CharField):

    def validate(self, value):
        super(Html5EmailField, self).validate(value)
        try:
            socket.getaddrinfo('google.cim', '9999')
        except socket.gaierror:
            raise ValidationError("This email address can't be valid")


class Html5EmailInput(Input): 
    input_type = 'email'