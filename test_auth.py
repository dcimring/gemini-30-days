import unittest
from app import app, db, User

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False # Not using WTF-Forms but good practice
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_signup_login(self):
        # 1. Sign up
        response = self.app.post('/signup', data=dict(
            username='testpirate',
            password='password123'
        ), follow_redirects=True)
        
        # Check if we are redirected to index (status 200 after redirect)
        self.assertEqual(response.status_code, 200)
        # Check if we see the index page content (e.g., "Pirate Translator")
        self.assertIn(b'Pirate Translator', response.data)
        # Check if we see the username
        self.assertIn(b'Ahoy, testpirate!', response.data)

        # 2. Logout
        response = self.app.get('/logout', follow_redirects=True)
        self.assertIn(b'Login', response.data)

        # 3. Login
        response = self.app.post('/login', data=dict(
            username='testpirate',
            password='password123'
        ), follow_redirects=True)
        self.assertIn(b'Ahoy, testpirate!', response.data)

    def test_signup_duplicate(self):
        # Create a user first
        with app.app_context():
            u = User(username='existing')
            u.set_password('pass')
            db.session.add(u)
            db.session.commit()

        # Try to sign up with same name
        response = self.app.post('/signup', data=dict(
            username='existing',
            password='newpass'
        ), follow_redirects=True)
        
        # Should show flash message
        self.assertIn(b'Username already exists', response.data)

if __name__ == '__main__':
    unittest.main()
