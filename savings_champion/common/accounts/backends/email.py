from django.contrib.auth import get_user_model

User = get_user_model()


class EmailAuthBackend(object):
    """
    Email Authentication Backend

    Allows a user to sign in using an email/password pair rather than
    a username/password pair.
    """

    def authenticate(self, email=None, password=None):
        """ Authenticate a user based on email address as the user name. """
        try:
            for user in User.objects.filter(email__iexact=email):
                if user.check_password(password):
                    return user
                return None
        except:
            return None

    def get_user(self, user_id):
        """ Get a User object from the user_id. """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None