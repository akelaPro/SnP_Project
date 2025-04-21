from .base import BaseService

class LogoutService:
    @classmethod
    def execute(cls, data):
        user = data['user']
        try:
            user.token.delete()
        except:
            pass