"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
from django.test import TestCase
from common.accounts.backends.email import EmailAuthBackend
from django.contrib.auth.models import User
        
class EmailAuthentication(TestCase):
    def setUp(self):
        self.emailAuth = EmailAuthBackend()
        self.user1 = User.objects.create_user('user1', 'user1@user.com', 'password')
        self.user2 = User.objects.create_user('user2', 'user2@user.com', 'PaSsWoRd!!.,')
        
    def test_authenticate(self):
        '''
        Tests on confirming a user can authenticate fine
        '''
        self.assertEqual(self.emailAuth.authenticate(self.user1.email, 'password'), self.user1, 'User 1 authenticated')
        self.assertEqual(self.emailAuth.authenticate('user2@user.com', 'PaSsWoRd!!.,'),self.user2, 'User 2 authenticated')
        
        self.assertEqual(self.emailAuth.authenticate(self.user1.email, 'bfeidoif'), None)
        self.assertEqual(self.emailAuth.authenticate('noemail@n.com', 'fakepassword'), None)
        
    
    def test_gest_user(self):
        '''
        Confirm the get_user method works
        '''
        self.assertEqual(self.emailAuth.get_user(self.user1.pk), self.user1)
        self.assertEqual(self.emailAuth.get_user(1000), None)
        
        
        
        
