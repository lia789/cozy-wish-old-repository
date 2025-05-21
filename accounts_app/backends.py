from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import DeletedAccount

User = get_user_model()

class CustomModelBackend(ModelBackend):
    """
    Custom authentication backend that checks if the email exists in the DeletedAccount model
    before authenticating.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user based on email/username and password.
        Check if the email exists in the DeletedAccount model first.
        """
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
            
        if username is None or password is None:
            return None
            
        # Check if the email exists in the DeletedAccount model
        if DeletedAccount.objects.filter(email=username).exists():
            return None
            
        # Continue with the standard ModelBackend authentication
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user.
            User().set_password(password)
            return None
            
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
