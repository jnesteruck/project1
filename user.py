class User:
    def __init__(self, user, fname, lname, address, passkey, admin=False):
        self._user = str(user)
        self._fname = str(fname)
        self._lname = str(lname)
        self._address = str(address)
        self._passkey = int(passkey)
        self._admin = bool(admin)
    
    def getUsername(self) -> str:
        return self._user

    def __str__(self):
        return "Name: " + self._fname + " " + self._lname + ", Username: " + self._user + ", Admin Access: " + str(self._admin)