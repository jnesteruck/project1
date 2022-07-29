class User:
    def __init__(self, user, name, address, passkey, admin=False):
        self._user = str(user)
        self._name = str(name)
        self._address = str(address)
        self._passkey = int(passkey)
        self._admin = bool(admin)
    
    def __str__(self):
        return "Name: " + self._name + ", Username: " + self._user + ", Admin Access: " + str(self._admin)