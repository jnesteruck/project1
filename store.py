from multiprocessing.sharedctypes import Value
import mysql.connector
import mysql_config as c
import re
import logging
from product import Product
from user import User

def main():

    logging.basicConfig(filename="store.log", level=logging.DEBUG, format='%(asctime)s :: %(message)s')
    
    try:
        cnx = mysql.connector.connect(user=c.user, password=c.password, host=c.host, database = "project1")
        cursor = cnx.cursor()
    except mysql.connector.Error as mce:
        print(mce.msg)
        logging.info("Database error occurred. Exiting program...")
        return
    except Exception as e:
        print("ERROR: Exiting program...")
        logging.info("Fatal error occurred. Exiting program...")
        return

    print("\nWelcome to the Music Store!\n\nAre you a returning customer? (Y/N)")
    uchoice = input("\n>>> ").lower()
    if uchoice == "n":
        addUser(cursor)

    user = login(cursor)
    viewCatalog(cursor)
    # viewOrderHistory(cursor, user)

def addOrder(cursor):
    '''
    addOrder


    '''
    pass

def viewOrderHistory(cursor, user):
    '''
    viewOrderHistory


    '''
    query = 'SELECT * FROM orders WHERE username = "' + user + '";'
    cursor.execute(query)
    print("")
    print("Order ID".ljust(9) + "| Order Date/Time\n------------------------------")
    for record in cursor:
        print((str(record[0]) + " ").rjust(9) + "| " + str(record[2]))
    
    print("\n--- END OF ORDER HISTORY ---\n")

def addUser(cursor):
    '''
    addUser()


    '''
    # username loop
    print("\nPlease choose a username.")
    while True:
        username = input("\nUsername: ")
        cursor.execute("SELECT username FROM customers;")
        in_use = False
        for record in cursor:
            if record == username:
                in_use = True
                break
        if in_use:
            print("Sorry, that username is already in use. Please pick a new username.")
            continue
        break
    # password loop
    print("Great! Now choose a password. Enter 1 for password rules.")
    while True:
        password = input("\nPassword: ")
        if password == "1":
            rules = "\n\t- Should be at least 8 characters\n\t- Should contain at least 1 digit (0-9)\n\t- Should contain at least 1 special character (. * ` ~ ! @ # $ % ^ & - _ + ?)\n\t- Should not contain spaces\n"
            print("\n\n" + "PASSWORD RULES".center(50,"*") + rules)
        if len(password) < 8:
            print("\nPassword must be at least 8 characters. Try again.")
            continue
        if re.search("\d", password) == None:
            print("\nPassword must contain at least 1 digit (0-9). Try again.")
            continue
        if re.search("[.*`~!@#$%^&\-_+?]", password) == None:
            print("\nPassword must contain at least 1 special character (. * ` ~ ! @ # $ % ^ & - _ + ?). Try again.")
            continue
        if re.search(" ", password) != None:
            print("\nPassword must not contain spaces. Try again.")
            continue
        break
    passkey = passKeyGenerator(password)

    # get the rest of the account info

    # name
    print("\nPlease enter your full name.")
    name = input("\nName: ")

    # address (we'll get it via a process to ensure formatting)
    print("\nPlease enter your street address. Do not include city, state, or ZIP Code information.")
    street = input("\nAddress: ")
    print("\nPlease enter your city.")
    city = input("\nCity: ")
    print("\nPlease enter your state. Enter '0' if not applicable.")
    state = input("\nState: ")
    print("\nPlease enter your ZIP Code.")
    zip = input("\nZIP Code: ")
    address = street + ", " + city + ", " + state + " " + zip

    user = User(username, name, address, passkey)
    



def editUser(cursor):
    '''
    editUser


    '''
    pass

def viewCatalog(cursor):
    '''
    viewCatalog

    Displays the store catalog to the user. Can filter by Experience or Category.

    Returns a bool. True if the catalog is viewed, False if the user quits.

    '''
    print("Which catalog would you like to view?")
    print("\tStarter catalog (1)")
    print("\tProfessional catalog (2)")
    print("\tAccessories (3)")
    print("\tEntire catalog (4)")
    print("\nEnter any other input to quit")
    choice = input("\n>>> ")
    query = "SELECT * FROM catalog"
    if choice == "1":
        query += " WHERE type1 = 'Starter'"
    elif choice == "2":
        query += " WHERE type1 = 'Pro'"
    elif choice == "3":
        query += " WHERE type1 = 'Accessories'"
    elif choice == "4":
        pass
    else:
        return False

    print("\tBand catalog (1)")
    print("\tOrchestra catalog (2)")
    print("\tPercussion catalog (3)")
    print("\tElectronics catalog (4)")
    print("\tGuitar, Bass Guitar, Piano (5)")
    print("\tEntire catalog (6)")
    print("\nEnter any other input to quit")
    choice2 = input("\n>>> ")

    if choice2 == "6":
        query += ";"
    else:
        if choice == "4":
            query += " WHERE "
        else:
            query += " AND "
        if choice2 == "1":
            query += "type2 = 'Band'"
        elif choice2 == "2":
            query += "type2 = 'Orchestra'"
        elif choice2 == "3":
            query += "type2 = 'Percussion'"
        elif choice2 == "4":
            query += "type2 = 'Electronics'"
        elif choice2 == "5":
            query += "type2 = 'Rhythm'"
        else:
            return False

    cursor.execute(query)

    print("")

    print("Product Name".ljust(25) + "| Sale Price".ljust(12) + " | Rental Price".ljust(16))
    print("|".rjust(26,"-") + "|".rjust(13,"-") + "---------------")

    for record in cursor:
        product = Product(record[1], record[2], record[3], record[4], record[5], record[6])
        print(product, "\n" + "|".rjust(26) + "|".rjust(13))
    print("\n")
    return True

def login(cursor):
    '''
    login

    Allows the user to enter their user information to log into their store account.

    Returns str (username)

    '''
    ucount = 0
    pcount = 0
    while True:
        print("\nPlease enter your username.\n")
        username = input("\nUsername: ")
        query = 'SELECT * FROM customers WHERE username = "' + username + '";'
        cursor.execute(query)
        for record in cursor:
            _user = record
        
        key = int(_user[3])
        if ucount >= 5:
            print("Couldn't find username after 5 attempts. Exiting program...")
            break
        if key == None:
            print("Sorry. Could not find username in system.")
            ucount += 1
            continue
        else:
            print("\nPlease enter your password.\n")
            password = input("\nPassword: ")
            ckey = passKeyGenerator(password)
            if pcount >= 5:
                print("\n5 Incorrect passsord attempts. Exiting program...")
            if ckey != key:
                print("\nSorry, that password is incorrect. Please try again\n")
                pcount += 1
            elif ckey == key:
                print("Login successful!")
                user = User(_user[0], _user[1], _user[2], _user[3], _user[4])
                return user



    pass

def searchKeyFile(char):
    with open("passKey.csv", "r") as f:
            for line in f:
                idx = int(line.split(",")[0])
                string = line.split(",")[1]
                if re.search(f'{char}', string):
                    return idx
    return None

def passKeyGenerator(password):
    '''
    passKeyGenerator


    '''
    half = len(password)//2
    p1 = password[:half]
    p2 = password[half:]
    n1 = 0
    n2 = 0
    for char in p1:
        n1 += searchKeyFile(char)
    for char in p2:
        n2 += searchKeyFile(char)
    return n1 * n2


    
if __name__ == "__main__":
    main()