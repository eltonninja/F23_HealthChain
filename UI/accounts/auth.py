from django.contrib.auth.backends import BaseBackend
from .models import NewUser
class EthereumAuthenticationBackend(BaseBackend):
    def authenticate(self, request, ethereum_account=None):
        try:
            return NewUser.objects.get(username=ethereum_account)
        except NewUser.DoesNotExist:
            return None
    def get_user(self, user_id):
        try:
            return NewUser.objects.get(pk=user_id)
        except NewUser.DoesNotExist:
            return None