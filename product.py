class Product:
    def __init__(self, name, type1, type2, sprice, rprice, stock):
        self._name = str(name)
        self._type1 = str(type1)
        self._type2 = str(type2)
        self._sprice = float(sprice)
        self._rprice = float(rprice)
        self._stock = int(stock)
    
    def setName(self, name):
        self._name = str(name)

    def setSalePrice(self, price):
        try:
            p = float(price)
        except ValueError as ve:
            print("**ERROR. PRICE MUST BE A NUMBER...**")
            return None
        self._sprice = p
    
    def setRentalPrice(self, price):
        try:
            p = float(price)
        except ValueError as ve:
            print("**ERROR. PRICE MUST BE A NUMBER...**")
            return None
        self._rprice = p

    def setStock(self, stock):
        try:
            s = int(stock)
        except ValueError as ve:
            print("**ERROR. STOCK MUST BE AN INTEGER...**")
            return None
        self._stock = s
    
    def getName(self):
        return self._name

    def getSalePrice(self):
        return self._sprice
    
    def getRentalPrice(self):
        return self._rprice
    
    def getStock(self):
        return self._stock
    
    def __str__(self):
        name = self._name
        if self._type1 == "Pro":
            name += " (Pro)"
        if self._stock == 0:
            return name.ljust(25) + "| " + f"\033[31m----- OUT OF STOCK -----\033[0m"
        else:
            if self._rprice == 0:
                return name.ljust(25) + "| $" + str(self._sprice).rjust(6) + "    | Not Available To Rent"
            else:
                return name.ljust(25) + "| $" + str(self._sprice).rjust(6) + "    | $" + str(self._rprice)