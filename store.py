import mysql.connector, re, os, logging
import mysql_config as c
import textFormat as tf
from product import Product
from user import User

# TODO:
# - Create addOrder() function
# - Create adminTools() function
# - Create editUser() function
# - Create removeUser() function

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
    
    # tf.fastPrint("".center(100, "-"), 2)
    # tf.slowPrint(" Welcome to the Music Store! ".center(100, "-"), 0.01)
    # tf.fastPrint("".center(100, "-"), 3)
    print("\nAre you a returning customer? (Y/N)")
    uchoice = input("\n>>> ").lower()
    if uchoice == "n":
        t_user = addUser(cursor)
    else:
        t_user = None
    user = login(cursor, t_user)

    options = {"0", "1", "2", "3", "4", "5", "6"}
    omax = 6

    while True:
        if type(user) != User:
            break
        username = user.getUsername()
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
        choice = input("\nMake your selection: ")
        if choice not in options:
            print(f"Please select a valid option (Enter a digit between 1 and {omax}")
        elif choice == "0":
            os.system("cls")
            print("\n")
            break
        elif choice == "1":
            viewCatalog(cursor)
        elif choice == "2":
            addOrder(user, cursor)
        elif choice == "3":
            viewOrderHistory(cursor, user)
        elif choice == "4":
            print(f"\nYour balance: ${round(user.getBalance(), 2)}\n")
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
    
    # Closing message
    if type(user) != User:
        print()
    else:
        print()
        tf.fastPrint("".center(200,"-"), 4)
        tf.slowPrint(" Thank you for visiting the music store! Have a wonderful day! ".center(200,"-"), 0.005)
        tf.fastPrint("".center(200,"-"), 5)
        print()

# TODO: NEEDS WORK
def addOrder(user,cursor):
    '''
    addOrder


    '''
    total = 0
    new_balance = user.changeBalance(total)
    cursor.execute(f"UPDATE customers SET balance = {new_balance} WHERE username = '{user.getUsername()}';")

# TODO: NEEDS WORK
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
    address = formatAddress()

    user = User(username, fname, lname, address, passkey, 0)

    # start transaction
    cursor.execute("START TRANSACTION;")
    query = f"INSERT INTO customers (username, firstName, lastName, address, passkey, balance, adminAccess) VALUES ('{username}', '{fname}', '{lname}', '{address}', {passkey}, 0, FALSE);"
    cursor.execute(query)
    # commit changes
    cursor.execute("COMMIT;")

    return user

# TODO: NEEDS WORK
def adminTools(cursor, user):
    '''
    adminTools
    
    
    '''
    if not user.isAdmin():
        print("Sorry. You do not have administrative access.")
        logging.info("Unauthorized attempt to reach administrative tools...")
        return None
    
def disableUser(cursor, user):
    '''
    disableUser
    
    Allows the user to disable their account from the database. Does not
    remove all data. Removes name, address, passkey, and balance.

    Returns True.

    '''
    # start transaction
    cursor.execute("START TRANSACTION;")
    cursor.execute(f"UPDATE customers SET firstName = 'DISABLED' WHERE username = '{user.getUsername()}';")
    user._fname = None
    cursor.execute(f"UPDATE customers SET lastName = NULL WHERE username = '{user.getUsername()}';")
    user._lname = None
    cursor.execute(f"UPDATE customers SET address = NULL WHERE username = '{user.getUsername()}';")
    user._address = None
    cursor.execute(f"UPDATE customers SET passkey = NULL WHERE username = '{user.getUsername()}';")
    user._passkey = None
    cursor.execute(f"UPDATE customers SET balance = NULL WHERE username = '{user.getUsername()}';")
    user._balance = None
    # commit changes
    cursor.execute("COMMIT;")
    pass

# TODO: NEEDS WORK
def enableUser(cursor, user):
    '''
    enableUser
    
    Allows the user to reenable their account in the database after disabling.

    '''
    cursor.execute(f"UPDATE customers SET firstName = 'DISABLED' WHERE username = '{user.getUsername()}';")
    user._fname = None
    cursor.execute(f"UPDATE customers SET lastName = NULL WHERE username = '{user.getUsername()}';")
    user._lname = None
    cursor.execute(f"UPDATE customers SET address = NULL WHERE username = '{user.getUsername()}';")
    user._address = None
    cursor.execute(f"UPDATE customers SET passkey = NULL WHERE username = '{user.getUsername()}';")
    user._passkey = None
    cursor.execute(f"UPDATE customers SET balance = NULL WHERE username = '{user.getUsername()}';")
    user._balance = None
    pass

def formatAddress():
    '''
    formatAddress
    
    Prompts user input to properly format their address for their record in the database
    
    '''
    print("\nPlease enter your street address. Do not include city, state, or ZIP Code information.\n")
    street = input("\nAddress: ")
    print("\nPlease enter your city.\n")
    city = input("\nCity: ").capitalize()
    print("\nPlease enter your state initials (e.g. New York = NY, Texas = TX, etc.).\n")
    state = input("\nState: ").capitalize()
    print("\nPlease enter your ZIP Code.\n")
    zip = input("\nZIP Code: ")

    return f"{street}, {city}, {state} {zip}"

def changeName(cursor, user):
    '''
    changeName
    
    Prompts user input to change name in database.
    
    '''
    # start transaction
    cursor.execute("START TRANSACTION;")

    print("\nPlease enter your first and last name. Please connect multiple last names using a dash (-).")
    ninp = input("\nName: ").split(" ")
    if len(ninp) == 1:
        fname, lname = ninp[0], ""
    else:
        fname, lname = ninp[0], ninp[-1]
    if [fname, lname] == user.getName():
        pass
    elif fname == user.getName(0):
        user.setName(last=lname)
        cursor.execute(f"UPDATE customers SET lastName = '{lname}' WHERE username='{user.getUsername()}';")
    elif lname == user.getName(1):
        user.setName(first=fname)
        cursor.execute(f"UPDATE customers SET firstName = '{fname}' WHERE username='{user.getUsername()}';")
    else:
        user.setName(fname, lname)
        cursor.execute(f"UPDATE customers SET firstName = '{fname}' WHERE username='{user.getUsername()}';")
        cursor.execute(f"UPDATE customers SET lastName = '{lname}' WHERE username='{user.getUsername()}';")
    
    # commit changes
    cursor.execute("COMMIT;")

def changePassword(cursor, user):
    '''
    changePassword
    
    Allows user to modify their password in the database.

    '''
    count = 0
    while True:
        print("\nEnter current password, or enter 'q' to quit:")
        curr_pass = input("\n>>> ")
        if curr_pass.lower() in {'q', 'quit'}:
            return None
        curr_key = passKeyGenerator(curr_pass, cursor)
        user_key = user.getPasskey()
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
    user.setPasskey(passkey)

    # start transaction
    cursor.execute("START TRANSACTION;")
    cursor.execute(f"UPDATE customers SET passkey = {passkey} WHERE username='{user.getUsername()}';")
    # commit changes
    cursor.execute("COMMIT;")
    
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
            continue
        elif len(password) < 8:
            print("\nPassword must be at least 8 characters. Try again.\n")
            continue
        elif re.search("\d", password) == None:
            print("\nPassword must contain at least 1 digit (0-9). Try again.\n")
            continue
        elif re.search("[.*`~!@#$%^&\-_+?]", password) == None:
            print("\nPassword must contain at least 1 special character (. * ` ~ ! @ # $ % ^ & - _ + ?). Try again.\n")
            continue
        elif re.search(" ", password) != None:
            print("\nPassword must not contain spaces. Try again.\n")
            continue
        break
    return passKeyGenerator(password, cursor)

# TODO: NEEDS WORK
def editUser(cursor, user):
    '''
    editUser

    Gives user access to their account settings.
    '''
    while True:
        print("\nPlease select an option from below:\n")
        print("\tView Balance (1)")
        print("\tAdd To Balance (2)")
        print("\tChange Address (3)")
        print("\tChange Name (4)")
        print("\tChange Password (5)")
        print("\tChange Username (6)")
        print("\tDisable account (7)")
        print("\tExit menu (0)")
        choice = input("\n>>> ")

        if choice == "0":
            return None
        elif choice == "1":
            print("\nYour balance: $" + str(user.getBalance()) + "\n")
        elif choice == "2":
            balance = user.addToBalance()
            cursor.execute(f"UPDATE customers SET balance = {balance} WHERE username='{user.getUsername()}';")
        elif choice == "3":
            user.setAddress(formatAddress())
            cursor.execute(f"UPDATE customers SET address = '{user.getAddress()}' WHERE username='{user.getUsername()}';")
        elif choice == "4":
            changeName()
        elif choice == "5":
            changePassword()
        elif choice == "6":
            pass
        elif choice == "7":
            print("\nAre you sure you want to disable your account? This will remove personal data but\nwill not remove your username or order history. You can reactivate your account later.")
            disable_choice = input("\nY/N: ").lower()
            if disable_choice in {"n", "no"}:
                disableUser(cursor, user)
            elif disable_choice in {"y", "yes"}:
                continue
            else:
                print("\nInvalid input. Returning to previous menu...")
                logging.info("Invalid input. Returning to account settings menu...")
                continue
        else:
            print("Please choose a valid option (0-7).")


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

    Returns user object

    '''
    if type(user) == User:
        print("\nWelcome to the music store! Thank you for creating an account with us!\n")
        return user
    ucount = 0
    pcount = 0
    while True:
        print("\nPlease enter your username.\n")
        username = input("\nUsername: ")
        query = f'SELECT username, firstName, lastName, address, passKey, balance, adminAccess FROM customers WHERE username = "{username}";'
        cursor.execute(query)
        for record in cursor:
            _user = record
            break
        
        key = int(_user[4])
        if ucount >= 5:
            tf.printNoLine("\nCouldn't find username after 5 attempts. Exiting program")
            tf.slowPrint("...", 0.5)
            logging.info("5 failed username attempts. Exiting program...")
            return None
        if key == None:
            print("Sorry. Could not find username in system.")
            ucount += 1
            continue
        else:
            print("\nPlease enter your password.\n")
            password = input("\nPassword: ")
            ckey = passKeyGenerator(password, cursor)
            if pcount >= 5:
                tf.printNoLine("\n5 Incorrect passsord attempts. Exiting program")
                tf.slowPrint("...", 0.5)
                return None
            if ckey != key:
                print("\nSorry, that password is incorrect. Please try again\n")
                pcount += 1
            elif ckey == key:
                print("\nLogin successful.")
                tf.pause(1)
                print("Welcome back!\n")
                if _user[6] == True:
                    user = User(_user[0], _user[1], _user[2], _user[3], _user[4], _user[5], True)
                else:
                    user = User(_user[0], _user[1], _user[2], _user[3], _user[4], _user[5])
                tf.pause(1)
                os.system("cls")
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