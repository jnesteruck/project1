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
        user = addUser(cursor)
    else:
        user = None
    while True:
        username = login(cursor, user)
        options = {"0", "1", "2", "3", "4", "5", "6"}
        omax = 6
        print("\nWhat would you like to do today?\n")
        print("\tView the catalog (1)")
        print("\tMake a purchase (2)")
        print("\tView Order History (3)")
        print("\tView account balance (4)")
        print("\tAdd to account balance (5)")
        print("\tAccount settings (6)")
        if user.isAdmin():
            print("\tAdmin Tools (7)")
            print("\tQuit (0)")
            options.add("7")
            omax = 7
        else:
            print("\tQuit(0)\n")
        choice = input("\nMake your selection: >>> ")
        if choice not in options:
            print(f"Please select a valid option (Enter a digit between 1 and {omax}")
        elif choice == "0":
            break
        elif choice == "1":
            viewCatalog(cursor)
        elif choice == "2":
            addOrder(user, cursor)
        elif choice == "3":
            viewOrderHistory(cursor, user)
        elif choice == "4":
            print("\nYour balance: $" + str(user.getBalance()) + "\n")
        elif choice == "5":
            balance = user.addToBalance()
            cursor.execute(f"UPDATE customers SET balance = {balance} WHERE username = '{username}'")
        elif choice == "6":
            editUser(cursor, user)
        elif choice == "7":
            admin_count = 0
            while True:
                print("\nPlease enter the admin password:\n")
                userpass = input("\nPassword: ")
                userkey = passKeyGenerator(userpass, cursor)
                cursor.execute(f"SELECT passkey FROM customers WHERE username = 'admin'")
                for record in cursor:
                    adminkey = record[0]
                if userkey != adminkey:
                    if admin_count >= 5:
                        print("\n5 incorrect password attempts. Exiting admin settings...\n")
                        logging.info("Unauthorized attempt to reach administrative tools...")
                        break
                    print("\nSorry, that password is incorrect, try again...\n")
                    admin_count += 1


            
                
            


def addOrder(user,cursor):
    '''
    addOrder


    '''
    total = 0
    new_balance = user.changeBalance(total)
    cursor.execute(f"UPDATE customers SET balance = {new_balance} WHERE username = '{user.getUsername()}';")

def viewOrderHistory(cursor, user):
    '''
    viewOrderHistory

    Allows user to view all orders they have made. Prints a table of their orders.

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

    Allows the user to create an account with the store interface in order to purchase products

    Returns a user object.

    '''
    # username loop
    print("\nPlease choose a username.\n")
    while True:
        username = input("\nUsername: ")
        cursor.execute("SELECT username FROM customers;")
        in_use = False
        for record in cursor:
            if record == username:
                in_use = True
                break
        if in_use:
            print("Sorry, that username is already in use. Please pick a different username.\n")
            continue
        break
    # password method
    print("Great! Now choose a password. Enter 1 for password rules.\n")
    passkey = createPassword(cursor)

    # get the rest of the account info

    # name
    print("\nPlease enter your first and last name. Please connect multiple last names using a dash (-).")
    ninp = input("\nName: ").split(" ")
    if len(ninp) == 1:
        fname, lname = ninp[0], ""
    else:
        fname, lname = ninp[0], ninp[-1]
    

    # address (we'll get it via a process to ensure formatting)
    print("\nPlease enter your street address. Do not include city, state, or ZIP Code information.\n")
    street = input("\nAddress: ")
    print("\nPlease enter your city.\n")
    city = input("\nCity: ")
    print("\nPlease enter your state. Enter '0' if not applicable.\n")
    state = input("\nState: ")
    print("\nPlease enter your ZIP Code.\n")
    zip = input("\nZIP Code: ")
    address = street + ", " + city + ", " + state + " " + zip

    user = User(username, fname, lname, address, passkey, 0)

    query = "INSERT INTO customers (username, firstName, lastName, address, passkey, balance, adminAccess) VALUES ('" + username + "', '" + fname + "', '" + lname + "', '" + address + "', " + passkey + ", 0, FALSE);"
    cursor.execute(query)

    return user

def adminTools(cursor, user):
    '''
    adminTools
    
    
    '''
    if not user.isAdmin():
        print("Sorry. You do not have administrative access.")
        logging.info("Unauthorized attempt to reach administrative tools...")
        return None
    

def removeUser(cursor, user):
    '''
    removeUser
    
    Allows the user to disable their account from the database. Does not
    remove 


    '''
    pass

def changePassword(cursor, user):
    '''
    changePassword
    
    Allows user to modify their password in the database.

    '''
    count = 0
    while True:
        print("\nEnter current password:")
        curr_pass = input("\n>>> ")
        curr_key = passKeyGenerator(curr_pass, cursor)
        cursor.execute(f"SELECT passkey FROM customers WHERE username='{user.getUsername()}';")
        for record in cursor:
            user_key = record[0]
        if curr_key != user_key:
            if count >= 5:
                print("5 incorrect password attempts. Returning to main menu...")
                return None
            print("Sorry, that password is incorrect, try again...")
            count += 1
            continue
        else:
            break
    passkey = createPassword(cursor)
    cursor.execute(f"UPDATE customers SET passkey = {passkey} WHERE username='{user.getUsername()}';")
    
def createPassword(cursor):
    '''
    createPassword
    
    Prompts user input to create a secure password.

    Returns the generated passkey.
    
    '''
    print("Great! Now choose a password. Enter 1 for password rules.\n")
    while True:
        password = input("\nPassword: ")
        if password == "1":
            rules = "\n\t- Should be at least 8 characters\n\t- Should contain at least 1 digit (0-9)\n\t- Should contain at least 1 special character (. * ` ~ ! @ # $ % ^ & - _ + ?)\n\t- Should not contain spaces\n"
            print("\n\n" + "PASSWORD RULES".center(50,"*") + rules)
        if len(password) < 8:
            print("\nPassword must be at least 8 characters. Try again.\n")
            continue
        if re.search("\d", password) == None:
            print("\nPassword must contain at least 1 digit (0-9). Try again.\n")
            continue
        if re.search("[.*`~!@#$%^&\-_+?]", password) == None:
            print("\nPassword must contain at least 1 special character (. * ` ~ ! @ # $ % ^ & - _ + ?). Try again.\n")
            continue
        if re.search(" ", password) != None:
            print("\nPassword must not contain spaces. Try again.\n")
            continue
        break
    return passKeyGenerator(password, cursor)

def editUser(cursor, user):
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

def login(cursor, user=None):
    '''
    login

    Allows the user to enter their user information to log into their store account.

    Returns str (username)

    '''
    if type(user) == User:
        print("\nWelcome to the music store! Thank you for creating an account with us!\n")
        return user.getUsername()
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
            ckey = passKeyGenerator(password, cursor)
            if pcount >= 5:
                print("\n5 Incorrect passsord attempts. Exiting program...")
            if ckey != key:
                print("\nSorry, that password is incorrect. Please try again\n")
                pcount += 1
            elif ckey == key:
                print("Login successful. Welcome back!")
                user = User(_user[0], _user[1], _user[2], _user[3], _user[4])
                return user

def passKeyGenerator(password, cursor):
    '''
    passKeyGenerator


    '''
    half = len(password)//2
    p1 = password[:half]
    p2 = password[half:]
    n1 = 0
    n2 = 0
    for char in p1:
        cursor.execute("SELECT * FROM passKeyDecoder;")
        for record in cursor:
            if re.search(f'{char}', record[1]) != None:
                n1 += record[0]
    for char in p2:
        cursor.execute("SELECT * FROM passKeyDecoder;")
        for record in cursor:
            if re.search(f'{char}', record[1]) != None:
                n2 += record[0]
    return n1 * n2


    
if __name__ == "__main__":
    main()