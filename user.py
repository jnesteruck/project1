import logging

logging.basicConfig(filename="store.log", level=logging.DEBUG, format='%(asctime)s :: %(message)s')

class User:
    def __init__(self, user, fname, lname, address, passkey, balance, admin=False):
        self._user = str(user)
        self._fname = str(fname)
        self._lname = str(lname)
        self._address = str(address)
        self._passkey = int(passkey)
        self._balance = float(balance)
        self._admin = bool(admin)
    
    def getUsername(self) -> str:
        '''
        getUsername
        
        Returns the user's username (string)
        
        '''
        return self._user
    
    def getBalance(self) -> float:
        '''
        getBalance
        
        Returns the user's balance (float)
        
        '''
        return self._balance
    
    def addToBalance(self):
        '''
        addToBalance

        Prompts user input to add to their account balance.

        '''
        while True:
            print("\nHow much would you like to add to your balance?\n")
            try:
                amount = round(float(input("Enter an amount (USD): $")), 2)
            except ValueError as ve:
                print("Invalid currency format.")
                logging.info("User failed to input a number in decimal format...")
            print(f"\nYou would like to add ${amount} to your balance? Confirm Y/N.")
            confirm = input("\n>>> ").lower()
            if confirm in {"n", "no"}:
                continue
            if type(amount) == float:
                self._balance += amount
                return self._balance
    
    def changeBalance(self, amt):
        '''
        changeBalance

        Allows the user's balance to be changed. Will add to balance
        if amt is positive and will remove if amt is negative. If
        balance drops below 0, transaction will not go through.

        Returns balance if funds are sufficient, returns None otherwise.
        '''
        if self._balance + amt < 0:
            print("Sorry, insufficient funds...")
            logging.info("User tried to make purchase that exceeded available funds...")
            return None
        self._balance += amt
        return self._balance


    def isAdmin(self) -> bool:
        '''
        isAdmin
        
        Returns the user's admin value (bool). Returns True if the
        user is an administrator, False otherwise.
        
        '''
        return self._admin

    def __str__(self):
        return "Name: " + self._fname + " " + self._lname + ", Username: " + self._user + ", Balance: " + str(self._balance)