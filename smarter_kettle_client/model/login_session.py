import datetime


class LoginSession:
    def __init__(self, data: dict):
        self.kind = data.get('kind')
        self.local_id = data.get('localId')
        self.email = data.get('email')
        self.display_name = data.get('displayName')
        self.id_token = data.get('idToken')
        self.registered = data.get('registered')
        self.refresh_token = data.get('refreshToken')
        self.expires_in = data.get('expiresIn')

        self.expires_at = datetime.datetime.now() + datetime.timedelta(0,
                                                                       int(self.expires_in))

    def is_expired(self) -> bool:
        return self.expires_at > datetime.datetime.now()
