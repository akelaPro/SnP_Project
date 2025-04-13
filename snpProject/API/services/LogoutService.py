from .base import BaseService

class LogoutService(BaseService):
    def process(self):
        user = self.data['user']
        try:
            user.token.delete()
        except:
            pass