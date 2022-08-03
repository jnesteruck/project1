from tkinter import Y
import mysql.connector, re, os, logging
import mysql_config as c
import textFormat as tf
from product import Product
from user import User
from getpass import getpass

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
    clear()
    fancy = False
    if fancy:
        tf.fastPrint("".center(200, "-"), 5)
        print()
        tf.fastPrint(" Welcome to the Music Store! ".center(200, "-"), 3, spd=0.02)
        print()
        tf.fastPrint("".center(200, "-"), 7)
        tf.pause(2)
        clear()
    print("Are you a returning customer? (Y/N)")
    uchoice = input("\n>>> ").lower()
    while True:
        if uchoice in {"q", "quit"}:
            t_user = 0
            break
        if uchoice in {"n", "no"}:
            # send user to account creation process. Returns user object so new user doesn't have to log in again.
            t_user = addUser(cursor)
            break
        elif uchoice in {"y", "yes"}:
            # None will send user to typical login process
            t_user = None
            break
        else:
            # check for invalid inputs
            print("\nInvalid input. Try again...\nEnter 'q' to quit")
            tf.pause(2)
            clear()
            print("\nAre you a returning customer? (Y/N)")
            uchoice = input("\n>>> ").lower()
            continue
    # login
    if t_user == 0:
        user = 0
    else:
        user = login(cursor, t_user)

    # check that user chooses an option correctly
    options = {"0", "1", "2", "3", "4", "5", "6", "7"}
    omax = 7
    cart = []

    while True:
        clear()
        if type(user) != User:
            break
        username = user.getUsername()
        print("What would you like to do today?\n")
        print("\tView the catalog (1)")
        print("\tMake a purchase (2)")
        print("\tReturn a rental (3)")
        print("\tView Order History (4)")
        print("\tView account balance (5)")
        print("\tAdd to account balance (6)")
        print("\tAccount settings (7)")
        if user.isAdmin():
            print("\tAdmin Tools (8)")
            print("\tQuit (0)")
            options.add("8")
            omax = 8
        else:
            print("\tQuit (0)\n")
        choice = input("\nMake your selection: ")
        if choice not in options:
            print(f"Please select a valid option (Enter a digit between 0 and {omax})")
        elif choice.lower() in {"0", "q", "quit"}:
            clear()
            break
        elif choice == "1":
            viewCatalog(cursor)
        elif choice == "2":
            if cart == []:
                cart = addOrder(user, cursor)
            else:
                cart = addOrder(user, cursor, cart)
        elif choice == "4":
            viewOrderHistory(cursor, user)
        elif choice == "5":
            # view balance
            clear()
            print(f"\nYour balance: ${'{:.2f}'.format(user.getBalance())}\n")
            tf.pause(1)
            input("\nPress enter to continue.\n")
        elif choice == "6":
            balance = user.addToBalance()
            # start transaction
            cursor.execute("START TRANSACTION;")
            cursor.execute(f"UPDATE customers SET balance = {balance} WHERE username = '{username}'")
            # commit changes
            cursor.execute("COMMIT;")
        elif choice == "7":
            editUser(cursor, user)
        elif choice == "8":
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
                else:
                    adminTools(cursor, user)
                    break
    
    # Closing message
    if type(user) != User:
        print()
    else:
        print()
        if fancy:
            tf.fastPrint("".center(200,"-"), 5)
            print()
            tf.fastPrint(" Thank you for visiting the music store! Have a wonderful day! ".center(200,"-"), 3, spd=0.02)
            print()
            tf.fastPrint("".center(200,"-"), 7)
            tf.pause(3)
            clear()

def addOrder(user,cursor, cart=[]):
    '''
    addOrder

    Allows user to purchase products from the catalog using their account balance.

    Returns cart if user has insufficient funds.

    '''
    clear()
    viewed = viewCatalog(cursor)
    if viewed == False:
        return
    if cart != []:
        print("You currently have items in your cart. Would you like to continue with these items, or clear your cart?\nEnter C to clear the cart, enter anything else to continue.")
        cart_choice = input("\n>>> ")
        if cart_choice.lower() == "c":
            cart = []
    while True:
        while True:
            print("\nWhat would you like to purchase today?\n\nEnter the Product ID for the product you want to purchase:\n")
            try:
                prod_id = int(input("\n>>> "))
            except ValueError:
                print("Please enter an appropriate Product ID.")
                logging.info("User failed to enter an integer for Product ID...")
                continue
            cursor.execute("SELECT ProductID FROM catalog;")
            id_list = []
            for record in cursor:
                id_list.append(record[0])
            if prod_id not in id_list:
                print("Please enter an appropriate Product ID.")
                logging.info("User entered an unassigned Product ID...")
                continue
            else:
                break
        cursor.execute(f"SELECT * FROM catalog WHERE ProductID={prod_id};")
        for record in cursor:
            prod = Product(record[0], record[1], record[2], record[3], record[4], record[5], record[6])
        if prod.getStock() == 0:
            print("\nSorry, this product is out of stock. Please make a different selection.\n")
            logging.info("User tried to buy a product that is out of stock...")
            continue
        if prod.getSalePrice() == 0:
            t = "p"
        else:
            while True:
                print("\nWill you be renting(R) or purchasing(P) today?\n")
                t = input("\n>>> ").lower()
                if len(t) != 1:
                    t = t[0]
                if t not in {"p", "r"}:
                    print("Please select a valid option (R for renting, P for purchasing).")
                    logging.info("Invalid user input for rental/purchase option...")
                    continue
                break
        while True:
            print(f"\nHow many {prod.getName()}s will you be getting?\n")
            try:
                quant = int(input("\n>>> "))
                if quant < 0:
                    raise Exception
                else:
                    break
            except ValueError:
                print("Please enter a valid integer.")
                logging.info("Invalid user input. Did not enter a positive integer for quantity...")
            except Exception:
                print("Value must be greater than 0.")
                logging.info("Invalid user input. Did not enter a positive value for quantity...")
        
        # add to cart
        cart.append((prod, quant, t))
        # clear terminal
        clear()
        
        # print cart
        print(" Your Cart ".center(100, "-"))
        pstatement = f'{"Product Name".ljust(25)}| Quantity | Total Price'
        print(f"\033[4m{pstatement}\033[0m")
        total = 0
        for elem in cart:
            if elem[2] == "r":
                price = elem[0].getRentalPrice()
            elif elem[2] == "p":
                price = elem[0].getSalePrice()
            print(f"{elem[0].getName().ljust(25)}|{str(elem[1]).rjust(9)} | ${str(round(elem[1] * price, 2))}")
            total += round(elem[1] * price, 2)
        print(f'{"|".rjust(37)} ${total}')

        while True:
            print("\nWould you like to add anything else to your purchase (Y/N)?\n")
            u_c = input("\n>>> ")
            if u_c not in {"y", "n", "yes", "no"}:
                print("\nPlease select a valid option (Y - yes, N - no).\n")
                logging.info("Invalid user input. Did not enter (Y/N) for binary question...")
                tf.pause(2)
                continue
            else:
                break

        if u_c in {"y", "yes"}:
            continue
        elif u_c in {"n", "no"}:
            break
    
    new_balance = user.changeBalance(-total)
    if new_balance == None:
        print("You do not have sufficient funds in your balance to make this purchase. Please add funds and try again later.")
        return cart
    # start transaction
    cursor.execute("START TRANSACTION;")
    # change database inventory
    for elem in cart:
        cursor.execute(f"UPDATE catalog SET stock = {elem[0].getStock()} WHERE ProductID={elem[0].getId()};")
    # change user balance
    cursor.execute(f"UPDATE customers SET balance = {new_balance} WHERE username = '{user.getUsername()}';")
    # commit changes
    cursor.execute("COMMIT;")
    return []

# TODO: NEEDS WORK
def returnRental(user, cursor):
    '''
    returnRental
    
    Allows the user to return an item they have been renting from the store.
    
    '''
    clear()
    print()

# TODO: NEEDS TESTING
def viewOrderHistory(cursor, user):
    '''
    viewOrderHistory

    Allows user to view all orders they have made. Prints a table of their orders.

    '''
    query = 'WITH t1 AS (SELECT OrderID, productName AS Product, quantity, (quantity * salePrice) AS Total FROM itemsSold JOIN catalog ON itemsSold.ProductID=catalog.ProductID)'
    query+= f'SELECT t1.OrderID, transactionTime, SUM(Total) FROM orders JOIN t1 ON t1.OrderID=orders.OrderID WHERE username="{user.getUsername()}" GROUP BY OrderID;'
    cursor.execute(query)
    valid_ids = []
    orderHist = []
    for record in cursor:
        valid_ids.append(record[0])
        orderHist.append(f'{str(record[0]).zfill(3).rjust(8)} | {str(record[1])} | ${round(record[2], 2)}')
    
    while True:
        clear()
        print("")
        print(f'Order ID | {"Order Date/Time".ljust(19)} | Order Total\n{"".ljust(45, "-")}')
        for elem in orderHist:
            print(elem)
        print(f"\n{' END OF ORDER HISTORY '.center(44, '-')}-\n")
        print("\nEnter an Order ID to view order details, or press enter to exit to the main menu.")
        id_in = input("\n>>> ")
        if id_in.isnumeric():
            id = int(id_in)
        else:
            break
        cursor.execute(f'SELECT * FROM itemsSold JOIN catalog ON itemsSold.ProductID=catalog.ProductID WHERE OrderID={id};')
        for record in cursor:
            if record is None:
                empty = True
            else:
                empty = False
        if id not in valid_ids or empty:
            print("\nNo such order in your history...\n")
        else:
            cursor.execute(f'SELECT productName AS Product, quantity, (quantity * salePrice) AS Total FROM itemsSold JOIN catalog ON itemsSold.ProductID=catalog.ProductID WHERE OrderID={id};')
            print(f'{"Product".ljust(25)} | Quantity | Price\n{"".ljust(50, "-")}')

            for record in cursor:
                print(f'{record[0].ljust(25)} | {str(record[1]).rjust(8)} | ${round(record[2], 2)}')
        tf.pause(3)
        input("\nPress enter to continue.")
        
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
            if record[0] == username:
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
    # additional layer of security
    if not user.isAdmin():
        print("Sorry. You do not have administrative access.")
        logging.info("Unauthorized attempt to reach administrative tools...")
        return None
    while True:
        clear()
        if type(user) != User:
            break
        options = {"1", "2", "3", "4", "5", "6", "0"}
        print("--- ADMINISTRATOR MENU ---\n")
        print("\tView All Orders (1)")
        print("\tView All Users (2)")
        print("\tAdd to catalog (3)")
        print("\tEdit Users (4)")
        print("\tPromote Users to Admin (5)")
        print("\tDisable Users (6)")
        print("\tExit to main menu (0)\n")
        choice = input("\nMake your selection: ")
        if choice not in options:
            print(f"Please select a valid option (Enter a digit between 0 and 6)")
        elif choice.lower() in {"0", "q", "quit"}:
            clear()
            break
        elif choice == "1":
            viewCatalog(cursor)
        elif choice == "2":
            if cart == []:
                cart = addOrder(user, cursor)
            else:
                cart = addOrder(user, cursor, cart)
        elif choice == "4":
            viewOrderHistory(cursor, user)
        elif choice == "5":
            # view balance
            clear()
            print(f"\nYour balance: ${'{:.2f}'.format(user.getBalance())}\n")
            tf.pause(1)
            input("\nPress enter to continue.\n")
        elif choice == "6":
            balance = user.addToBalance()
            # start transaction
            cursor.execute("START TRANSACTION;")
            cursor.execute(f"UPDATE customers SET balance = {balance} WHERE username = '{username}'")
            # commit changes
            cursor.execute("COMMIT;")
        elif choice == "7":
            editUser(cursor, user)
    
def disableUser(cursor, user):
    '''
    disableUser
    
    Allows the user to disable their account from the database. Does not
    remove all data. Removes name, address, and balance. Keeps username
    and passkey for later reactivation. Admin accounts cannot be disabled
    without removing admin access.

    Returns True.

    '''
    if user.isAdmin():
        print("Cannot disable admin account. Returning to menu...")
        logging.info("User attempted to disable account without removing admin privileges...")
        return
    # start transaction
    cursor.execute("START TRANSACTION;")
    cursor.execute(f"UPDATE customers SET firstName = 'DISABLED' WHERE username = '{user.getUsername()}';")
    user._fname = None
    cursor.execute(f"UPDATE customers SET lastName = NULL WHERE username = '{user.getUsername()}';")
    user._lname = None
    cursor.execute(f"UPDATE customers SET address = NULL WHERE username = '{user.getUsername()}';")
    user._address = None
    cursor.execute(f"UPDATE customers SET balance = NULL WHERE username = '{user.getUsername()}';")
    user._balance = None
    # commit changes
    cursor.execute("COMMIT;")

def enableUser(cursor, username):
    '''
    enableUser
    
    Allows the user to reenable their account in the database after disabling.

    '''
    cursor.execute(f"SELECT passkey FROM customers WHERE username='{username}';")
    key = 0
    for record in cursor:
        key = record[0]
    print("\nPlease enter your password:\n")
    while True:
        passw = input("\n>>> ")
        if passw.lower() in {"q", "quit"}:
            return
        nkey = passKeyGenerator(passw, cursor)
        if nkey != key:
            print("\nSorry, that password is incorrect. Try again.\nIf you don't remember your password, you will need to contact an admin for help.\n")
            print("Enter Q to quit.")
            continue
        else:
            break
    
    # start transaction
    cursor.execute("START TRANSACTION;")
    # name
    print("\nPlease enter your first and last name. Please connect multiple last names using a dash (-).")
    ninp = input("\nName: ").split(" ")
    if len(ninp) == 1:
        fname, lname = ninp[0], ""
    else:
        fname, lname = ninp[0], ninp[-1]
    cursor.execute(f"UPDATE customers SET firstName = '{fname}', lastName = '{lname}' WHERE username='{username}'")

    # address (we'll get it via a process to ensure formatting)
    address = formatAddress()
    cursor.execute(f"UPDATE customers SET address = '{address}' WHERE username='{username}'")

    user = User(username, fname, lname, address, nkey, 0)

    # commit changes
    cursor.execute("COMMIT;")

    return user

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
    clear()
    print("\nEnter current password, or enter 'q' to quit:")
    while True:
        curr_pass = getpass("\n>>> ")
        if curr_pass.lower() in {'q', 'quit'}:
            return None
        curr_key = passKeyGenerator(curr_pass, cursor)
        user_key = user.getPasskey()
        if curr_key != user_key:
            clear()
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

def changeUsername(cursor, user):
    '''
    changeUsername
    
    Allows user to modify their username in the database.

    '''
    clear()
    # username loop
    print("\nPlease choose a username, or enter 'q' to quit.\n")
    while True:
        username = input("\nUsername: ")
        if username.lower() in {'q', 'quit'}:
            return None
        cursor.execute("SELECT username FROM customers;")
        in_use = False
        for record in cursor:
            if record[0] == username:
                in_use = True
                break
        if in_use:
            clear()
            print("Sorry, that username is already in use. Please pick a different username.\n")
            continue
        break
    count = 0
    clear()
    print("\nEnter current password, or enter 'q' to quit.\n")
    while True:
        curr_pass = getpass("\nPassword: ")
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

    # start transaction
    cursor.execute("START TRANSACTION;")
    cursor.execute(f"UPDATE customers SET username = {username} WHERE username='{user.getUsername()}';")
    user.setUsername(username)
    # commit changes
    cursor.execute("COMMIT;")

def createPassword(cursor):
    '''
    createPassword
    
    Prompts user input to create a secure password.

    Returns the generated passkey.
    
    '''
    clear()
    print("Great! Now choose a password. Enter 1 for password rules.\n")
    while True:
        password = getpass("\nPassword: ")
        if password == "1":
            clear()
            rules = "\n\t- Should be at least 8 characters\n\t- Should contain at least 1 digit (0-9)\n\t- Should contain at least 1 special character (. * ` ~ ! @ # $ % ^ & - _ + ?)\n\t- Should not contain spaces\n"
            print("\n\n" + "PASSWORD RULES".center(50,"*") + rules)
            continue
        elif len(password) < 8:
            clear()
            print("\nPassword must be at least 8 characters. Try again.\n")
            continue
        elif re.search("\d", password) == None:
            clear()
            print("\nPassword must contain at least 1 digit (0-9). Try again.\n")
            continue
        elif re.search("[.*`~!@#$%^&\-_+?]", password) == None:
            clear()
            print("\nPassword must contain at least 1 special character (. * ` ~ ! @ # $ % ^ & - _ + ?). Try again.\n")
            continue
        elif re.search(" ", password) != None:
            clear()
            print("\nPassword must not contain spaces. Try again.\n")
            continue
        break
    return passKeyGenerator(password, cursor)

def editUser(cursor, user):
    '''
    editUser

    Gives user access to their account settings.
    '''
    clear()
    while True:
        print("Please select an option from below:\n")
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
            # view balance
            clear()
            print(f"\nYour balance: ${'{:.2f}'.format(user.getBalance())}\n")
            tf.pause(1)
            input("\nPress enter to continue.\n")
        elif choice == "2":
            # add to  balance
            balance = user.addToBalance()
            # start transaction
            cursor.execute("START TRANSACTION;")
            cursor.execute(f"UPDATE customers SET balance = {balance} WHERE username='{user.getUsername()}';")
            # commit changes
            cursor.execute("COMMIT;")
        elif choice == "3":
            # change address
            user.setAddress(formatAddress())
            # start transaction
            cursor.execute("START TRANSACTION;")
            cursor.execute(f"UPDATE customers SET address = '{user.getAddress()}' WHERE username='{user.getUsername()}';")
            # commit changes
            cursor.execute("COMMIT;")
        elif choice == "4":
            changeName()
        elif choice == "5":
            changePassword()
        elif choice == "6":
            changeUsername()
        elif choice == "7":
            print("\nAre you sure you want to disable your account? This will remove personal data but\nwill not remove your username or order history. You can reactivate your account later.")
            disable_choice = input("\nY/N: ").lower()
            if disable_choice in {"y", "yes"}:
                disableUser(cursor, user)
            elif disable_choice in {"n", "no"}:
                continue
            else:
                print("\nInvalid input. Returning to previous menu...")
                logging.info("Invalid input. Returning to account settings menu...")
                continue
        else:
            print("Please choose a valid option (0-7).")
            logging.info("User entered invalid input...")
            continue

def viewCatalog(cursor):
    '''
    viewCatalog

    Displays the store catalog to the user. Can filter by Experience or Category.

    Returns False if catalog is not viewed.

    '''
    clear()
    print("Which catalog would you like to view?\n")
    print("\tStarter catalog (1)")
    print("\tProfessional catalog (2)")
    print("\tAccessories (3)")
    print("\tEntire catalog (0)")
    print("\nEnter any other input to return to previous menu.")
    choice = input("\n>>> ")
    query = "SELECT * FROM catalog"
    if choice == "1":
        query += " WHERE type1 = 'Starter'"
    elif choice == "2":
        query += " WHERE type1 = 'Pro'"
    elif choice == "3":
        query += " WHERE type1 = 'Accessories'"
    elif choice == "0":
        pass
    else:
        return False

    clear()
    print("Select a filter:\n")
    print("\tBand catalog (1)")
    print("\tOrchestra catalog (2)")
    print("\tPercussion catalog (3)")
    print("\tElectronics catalog (4)")
    print("\tGuitar, Bass Guitar, Piano (5)")
    print("\tEntire catalog (0)")
    print("\nEnter any other input to return to previous menu.")
    choice2 = input("\n>>> ")

    if choice2 == "0":
        query += ";"
    else:
        if choice == "0":
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

    clear()
    cursor.execute(query)

    print(f'{"Product Name".ljust(25)}| ID  | Sale Price | {"Rental Price".ljust(15)}')
    print("|".rjust(26,"-") + "|".rjust(6,"-") + "|".rjust(13,"-") + "".center(15,"-"))

    for record in cursor:
        tf.pause(0.05)
        product = Product(record[0], record[1], record[2], record[3], record[4], record[5], record[6])
        print(product, "\n" + "|".rjust(26) + "|".rjust(6) + "|".rjust(13))
    print("\n")
    tf.pause(5)
    input("\nPress Enter to exit catalog.")
    
def login(cursor, user=None):
    '''
    login

    Allows the user to enter their user information to log into their store account.

    Returns user object

    '''
    clear()
    if type(user) == User:
        print("\nWelcome to the music store! Thank you for creating an account with us!\n")
        return user
    ucount = 0
    pcount = 0
    print("Please enter your username.\n")
    while True:
        if ucount > 5:
            tf.pause(1)
            print("Couldn't find username after 5 attempts.")
            tf.pause(1)
            tf.slowPrint("\nExiting program", 0.02)
            tf.pause(1)
            tf.slowPrint("...", 0.5)
            print()
            logging.info("5 failed username attempts. Exiting program...")
            return None
        username = input("\nUsername: ")
        query = f'SELECT username, firstName, lastName, address, passKey, balance, adminAccess FROM customers WHERE username = "{username}";'
        cursor.execute(query)
        _user = None
        for record in cursor:
            if record is None:
                pass
            else:
                _user = record
        if _user is None:
            clear()
            if ucount < 5:
                print(f"Sorry. Could not find username in system. Please try again. {5 - ucount} attempt(s) remaining.\n")
            ucount += 1
            continue
        else:
            if _user[1] == "DISABLED":
                print("\nPlease reactivate your account.\n")
                tf.pause(3)
                enableUser(cursor, username)
            key = int(_user[4])
            clear()
            print("Please enter your password.\n")
            while True:
                password = getpass("\nPassword: ")
                ckey = passKeyGenerator(password, cursor)
                if pcount >= 5:
                    tf.pause(1)
                    print("5 Incorrect passsord attempts.")
                    tf.pause(1)
                    tf.slowPrint("\nExiting program", 0.02)
                    tf.pause(1)
                    tf.slowPrint("...", 0.5)
                    print()
                    return None
                if ckey != key:
                    clear()
                    pcount += 1
                    print(f"Sorry, that password is incorrect. Please try again. {6 - pcount} attempt(s) remaining.\n")
                elif ckey == key:
                    clear()
                    print("Login successful.\n")
                    tf.pause(1)
                    print("Welcome back!\n")
                    if _user[6] == True:
                        user = User(_user[0], _user[1], _user[2], _user[3], _user[4], _user[5], True)
                    else:
                        user = User(_user[0], _user[1], _user[2], _user[3], _user[4], _user[5])
                    tf.pause(1)
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

def clear():
    os.system("cls")

if __name__ == "__main__":
    main()