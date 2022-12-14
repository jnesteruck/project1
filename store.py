from tkinter import Y
import mysql.connector, re, os, logging, datetime
import mysql_config as c
import textFormat as tf
from product import Product
from user import User
from getpass import getpass

yes = {"y", "yes"}
no = {"n", "no"}
fancy = True

def main():

    logging.basicConfig(filename="store.log", level=logging.DEBUG, format='%(asctime)s :: %(message)s')
    
    try:
        cnx = mysql.connector.connect(user=c.user, password=c.password, host=c.host, database = "project1")
        cursor = cnx.cursor()
    except mysql.connector.Error as mce:
        print(mce.msg)
        logging.info(mce.msg)
        logging.info("Database error occurred. Exiting program...")
        return
    except Exception as e:
        print("ERROR: Exiting program...")
        logging.info("Fatal error occurred. Exiting program...")
        return
    clear()
    if fancy:
        tf.fastPrint("".center(200, "-"), 5)
        print()
        tf.fastPrint(" Welcome to the Music Depot! ".center(200, "-"), 3, spd=0.02)
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
        elif uchoice in no:
            # send user to account creation process. Returns user object so new user doesn't have to log in again.
            t_user = addUser(cursor)
            break
        elif uchoice in yes or uchoice == 'admin':
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
            tf.pause(2)
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
        elif choice == "3":
            returnRental(user, cursor)
        elif choice == "4":
            viewOrderHistory(cursor, user)
        elif choice == "5":
            # view balance
            clear()
            print(f"\nYour balance: ${'{:.2f}'.format(user.getBalance())}\n")
            tf.pause(1)
            input("\nPress enter to continue.\n")
        elif choice == "6":
            clear()
            curr_bal = user.getBalance()
            print(f"Your balance: ${'{:.2f}'.format(curr_bal)}\n")
            balance = user.addToBalance()
            # start transaction
            cursor.execute("START TRANSACTION;")
            cursor.execute(f"UPDATE customers SET balance = {balance} WHERE username = '{username}'")
            # commit changes
            cursor.execute("COMMIT;")
            clear()
            chng = balance - curr_bal
            print(f"Successfully added ${'{:.2f}'.format(chng)} to your account!")
            tf.pause(2)
        elif choice == "7":
            editUser(cursor, user)
        elif choice == "8":
            admin_count = 0
            clear()
            while True:
                print("Please enter the admin password:\n")
                userpass = getpass("\nPassword: ")
                userkey = passKeyGenerator(userpass, cursor)
                cursor.execute(f"SELECT passkey FROM customers WHERE username = 'admin'")
                for record in cursor:
                    adminkey = record[0]
                if userkey != adminkey:
                    clear()
                    if admin_count >= 5:
                        print("5 incorrect password attempts. Exiting admin settings to main menu...\n")
                        logging.info("Unauthorized attempt to reach administrative tools...")
                        tf.pause(2)
                        break
                    print(f"Sorry, that password is incorrect. {5 - admin_count} attempts remaining, try again...\n")
                    admin_count += 1
                else:
                    adminTools(cursor, user)
                    break
    
    cursor.close()
    cnx.close()
    # Closing message
    if type(user) != User:
        print()
    else:
        print()
        if fancy:
            tf.fastPrint("".center(200,"-"), 5)
            print()
            tf.fastPrint(" Thank you for visiting the Music Depot! Have a wonderful day! ".center(200,"-"), 3, spd=0.02)
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
    if cart != []:
        print("You currently have items in your cart. Would you like to continue with these items, or clear your cart?\nEnter C to clear the cart, enter anything else to continue.")
        cart_choice = input("\n>>> ")
        if cart_choice.lower() == "c":
            cart = []
    while True:
        clear()
        viewed = viewCatalog(cursor)
        if viewed == False:
            break
        while True:
            print("\nWhat would you like to purchase today?\n\nEnter the Product ID for the product you want to purchase:\n")
            try:
                prod_id = int(input("\n>>> "))
            except ValueError:
                print("Please enter an appropriate Product ID.")
                logging.info("User failed to enter an integer for Product ID...")
                continue
            cursor.execute("SELECT ProductID FROM catalog;")
            logging.info("User accessed catalog table in project1 database...")
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
        logging.info("User accessed catalog table in project1 database...")
        for record in cursor:
            prod = Product(record[0], record[1], record[2], record[3], record[4], record[5], record[6])
        if prod.getStock() == 0:
            print("\nSorry, this product is out of stock. Please make a different selection.\n")
            logging.info("User tried to buy a product that is out of stock...")
            tf.pause(3)
            continue
        if prod.getRentalPrice() == 0:
            t = False
        else:
            while True:
                print("\nWill you be renting(R) or purchasing(P) today?\n")
                t_in = input("\n>>> ").lower()
                if len(t_in) != 1:
                    t_in = t_in[0]
                if t_in not in {"p", "r"}:
                    print("Please select a valid option (R for renting, P for purchasing).")
                    logging.info("Invalid user input for rental/purchase option...")
                    continue
                if t_in == 'p':
                    t = False
                elif t_in == 'r':
                    t = True
                break
        while True:
            if prod.getName()[-1] == "s":
                n = prod.getName()[0:-1]
            else:
                n = prod.getName()
            print(f"\nHow many {n}s will you be getting?\n")
            try:
                quant = int(input("\n>>> "))
                if quant < 0:
                    raise Exception
                elif quant == 0:
                    clear()
                    print("Exiting to main menu...")
                    return cart
                else:
                    break
            except ValueError:
                print("Please enter a valid integer.")
                logging.info("Invalid user input. Did not enter a positive integer for quantity...")
                continue
            except Exception:
                print("Value must be greater than 0.")
                logging.info("Invalid user input. Did not enter a positive value for quantity...")
                continue
        
        # add to cart
        prod.setStock(prod.getStock() - 1)
        cart.append((prod, quant, t))
        # clear terminal
        clear()
        
        # print cart
        print(" Your Cart ".center(100, "-"))
        pstatement = f'{"Product Name".ljust(25)}| Quantity | Total Price'
        print(f"\033[4m{pstatement}\033[0m")
        total = 0
        for elem in cart:
            if elem[2]:
                price = elem[0].getRentalPrice()
            else:
                price = elem[0].getSalePrice()
            print(f"{elem[0].getName().ljust(25)}|{str(elem[1]).rjust(9)} | ${str(round(elem[1] * price, 2))}")
            total += round(elem[1] * price, 2)
        print(f'{"|".rjust(37)} ${total}')

        while True:
            print("\nWould you like to add anything else to your purchase (Y/N)?\n")
            u_c = input("\n>>> ")
            if u_c not in yes and u_c not in no:
                print("\nPlease select a valid option (Y - yes, N - no).\n")
                logging.info("Invalid user input. Did not enter (Y/N) for binary question...")
                tf.pause(2)
                continue
            else:
                break

        if u_c in yes:
            continue
        elif u_c in no:
            break
    
    # if user quits out of the catalog without viewing it or putting items in their cart, they will return to main menu
    if cart == []:
        return cart

    new_balance = user.changeBalance(-total)
    if new_balance == None:
        print("You do not have sufficient funds in your balance to make this purchase. Please add funds and try again later.")
        logging.info("User tried to make a purchase without sufficient funds...")
        tf.pause(2)
        input("\nPress enter to continue.")
        return cart
    # start transaction
    o_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("START TRANSACTION;")
    # change database inventory
    try:
        cursor.execute(f"INSERT INTO orders (username, transactionTime) VALUES ('{user.getUsername()}', '{o_time}')")
        logging.info("Program inserted data into orders table in project1 database...")
        cursor.execute(f"SELECT orderID FROM orders WHERE username='{user.getUsername()}' AND transactionTime='{o_time}'")
        logging.info("Program accessed orders table in project1 database...")
        o_id = None
        for record in cursor:
            if record is None:
                print("Fatal Error. Returning to menu...")
                logging.info("Order not detected. Order aborted. Returning to menu...")
                tf.pause(2)
                return []
            else:
                o_id = record[0]
        for elem in cart:
            if elem[2]:
                price = elem[1] * elem[0].getRentalPrice()
            else:
                price = elem[1] * elem[0].getSalePrice()
            cursor.execute(f"INSERT INTO itemsSold (OrderID, ProductID, quantity, rented, price) VALUES ({o_id}, {elem[0].getId()}, {elem[1]}, {elem[2]}, {price});")
            cursor.execute(f"UPDATE catalog SET stock = {elem[0].getStock()} WHERE ProductID={elem[0].getId()};")
        # change user balance
        cursor.execute(f"UPDATE customers SET balance = {new_balance} WHERE username = '{user.getUsername()}';")
        logging.info("Program inserted data into itemsSold table in project1 database...")
        logging.info("Program updated catalog table in project1 database...")
        logging.info("Program updated customers table in project1 database...")
    except mysql.connector.Error as mce:
        print(mce.msg)
        logging.info(mce.msg)
        tf.pause(3)
        return cart
    # commit changes
    cursor.execute("COMMIT;")
    logging.info("User purchase successful...")
    return []

def returnRental(user, cursor):
    '''
    returnRental
    
    Allows the user to return an item they have been renting from the store.
    
    '''
    while True:
        clear()
        print("Please enter your Unit ID below. Enter 'q' to quit.")
        u_in = input("\nUnit ID: ")
        if u_in.lower() in {'q', 'quit'}:
            return
        try:
            uID = int(u_in)
            break
        except ValueError:
            print("Unit ID must be an integer. Try again...")
            logging.info("User tried to input a non-integer for Unit ID...")
            tf.pause(2)
            continue
        except Exception:
            print("Unknown error. Try again...")
            logging.info("Unknown error...")
            tf.pause(2)
            continue
    cursor.execute(f"SELECT productID, quantity FROM itemsSold WHERE UnitID={uID};")
    pID = None
    for record in cursor:
        if record is None:
            pass
        else:
            pID = record[0]
            q = record[1]
            break
    if pID is None:
        print("No such Unit ID. Try again...")
        logging.info("User entered invalid Unit ID. Returning to menu...")
        tf.pause(2)
        return
    cursor.execute(f"SELECT productName, stock FROM catalog WHERE ProductID={pID};")
    pname = None
    for record in cursor:
        if record is None:
            pass
        else:
            pname = record[0]
            pstock = record[1]
            break
    if pname is None:
        print("No such product. Try again...")
        logging.info("User entered invalid Product ID. Returning to menu...")
        tf.pause(2)
        return
    if q > 1 and pname[-1] == 's':
        prod_str = f'{q} {pname}'
    elif q > 1:
        prod_str = f'{q} {pname}s'
    elif q == 1:
        prod_str = pname

    stock = pstock + q
    print(f"Thank you, {user.getName(0)}, for returning your {prod_str}!")
    tf.pause(2)
    print("We hope you have a wonderful day!")
    # start transaction
    cursor.execute("START TRANSACTION;")
    # update stock inventory
    cursor.execute(f"UPDATE catalog SET stock = {stock} WHERE ProductID={pID};")
    logging.info("Program updated catalog table in project1 database...")
    # update unit info
    cursor.execute(f"UPDATE itemsSold SET rented = FALSE WHERE UnitID={uID};")
    logging.info("Program updated itemsSold table in project1 database...")
    # commit changes
    cursor.execute("COMMIT;")
    tf.pause(2)

def viewRentals(user, cursor):
    '''
    viewRentals
    
    
    Allows user to access database to see outstanding rentals
    
    '''
    query2 = f'WITH t1 AS (SELECT UnitID, ProductID, transactionTime, quantity FROM itemsSold LEFT JOIN orders on itemsSold.orderID=orders.orderID WHERE username="{user.getUsername()}" AND rented=True) SELECT UnitID, productName, quantity, (rentalPrice * quantity), transactionTime FROM t1 JOIN catalog ON t1.productID=catalog.productID;'
    print(f"Unit ID | {'Product'.ljust(25)} | Rented | Total   | Transaction Date/Time")
    cursor.execute(query2)
    for record in cursor:
        if record is None:
            print(" END OF RENTAL HISTORY ".center(45, '-'))
            break
        print(f"{str(record[0]).zfill(3).rjust(7)} | {record[1].ljust(25)} | {str(record[2]).rjust(6)} | ${('{:.2f}'.format(record[3])).rjust(6)} | {record[4]}")
    logging.info("Program accessed itemsSold, orders, and catalog tables in project1 database...")
    tf.pause(2)
    input("\nPress enter to return to menu.")

def viewOrderHistory(cursor, user):
    '''
    viewOrderHistory

    Allows user to view all orders they have made. Prints a table of their orders.

    '''
    query = f'SELECT orders.OrderID, transactionTime, SUM(price) FROM orders JOIN itemsSold ON itemsSold.OrderID=orders.OrderID WHERE username="{user.getUsername()}" GROUP BY OrderID;'
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
        print("\nEnter an Order ID to view order details, enter 'r' to view outstanding rentals, or press enter to exit to the main menu.")
        id_in = input("\n>>> ")
        if 'r' in id_in.lower():
            viewRentals(user, cursor)
            break
        elif id_in.isnumeric():
            id = int(id_in)
            cursor.execute(f'SELECT * FROM itemsSold JOIN catalog ON itemsSold.ProductID=catalog.ProductID WHERE OrderID={id};')
            for record in cursor:
                if record is None:
                    empty = True
                else:
                    empty = False
        else:
            break
        if id not in valid_ids or empty:
            print("\nNo such order in your history...\n")
        else:
            cursor.execute(f'SELECT productName AS Product, quantity, price FROM itemsSold JOIN catalog ON itemsSold.ProductID=catalog.ProductID WHERE OrderID={id};')
            print(f'{"Product".ljust(25)} | Quantity | Price\n{"".ljust(50, "-")}')

            for record in cursor:
                print(f'{record[0].ljust(25)} | {str(record[1]).rjust(8)} | ${round(record[2], 2)}')
        tf.pause(1)
        input("\nPress enter to continue.")
        logging.info("User succesfully viewed order history...")
        
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
    logging.info(f"User {username} has been added to the database...")

    return user

def addItem(cursor):
    '''
    addItem
    
    *ONLY ACCESSIBLE BY ADMIN*
    Allows user to add additional products to the catalog.
    
    '''
    items = []
    i = 0
    # add item to catalog
    while True:
        clear()
        # item name
        print("What item are you adding?")
        item_name = input("\n>>> ")
        clear()
        # item category
        print("What type of item is this?\n")
        print("\t(e.g. Band, Orchestra, Electronics, Percussion, etc.)")
        item_t2 = input("\n>>> ")
        # item experience level
        while True:
            print("\nWhat experience level is this item geared for? Choose from below.\n")
            print("\tStarter (1)")
            print("\tProfessional (2)")
            print("\tN/A (For accessory items) (3)")
            u_in1 = input("\n>>> ")
            if u_in1 == "1":
                item_t1 = "Starter"
            elif u_in1 == "2":
                item_t1 = "Pro"
            elif u_in1 == "3":
                item_t1 = "Accessories"
            else:
                print("Please select a valid option (1, 2, or 3).")
                logging.info("Admin input improper selection...")
                continue
            break
        # item price(s)
        while True:
            clear()
            s = False
            print("\nWhat is the sale price of this item?")
            u_in = input("\n>>> ")
            for elem in u_in.split("."):
                if not elem.isnumeric():
                    print("ERROR: Input must be numeric.") #print statement
                    logging.info("Invalid user input. Did not enter a numeric value for price...") # log this error
                    s = True
                    break
            if s:
                tf.pause(1.5) # pause for a bit
                continue
            item_sprice = float(u_in)
            break
        while True:
            clear()
            print("Will this item be available to rent? (Y/N)")
            achoice = input("\n>>> ").lower()
            if achoice in yes:
                while True:
                    r = False
                    clear()
                    print("What is the rental price (per month) of this item?")
                    u_in2 = input("\n>>> ")
                    for elem in u_in2.split("."):
                        if not elem.isnumeric():
                            print("ERROR: Input must be numeric.") #print statement
                            logging.info("Invalid user input. Did not enter a numeric value for price...") # log this error
                            r = True
                    if r:
                        tf.pause(1.5) # pause for a bit
                        continue
                    item_rprice = float(u_in2)
                    break
                break
            elif achoice in no:
                item_rprice = 0
                break
            else:
                print("\nPlease select a valid option (Y - yes, N - no).")
                logging.info("Admin entered invalid input for binary (Y/N) selection...")
                continue
        # item stock
        while True:
            clear()
            print("How much of this item will be in stock?")
            u_in3 = input("\n>>> ")
            if not u_in3.isnumeric():
                print("ERROR: Input must be numeric.") #print statement
                logging.info("Invalid user input. Did not enter an integer value for stock availablity...") # log this error
                continue
            item_stock = int(u_in3)
            break
        product = Product(i, item_name, item_t1, item_t2, item_sprice, item_rprice, item_stock)
        items.append(product)
        i += 1
        while True:
            clear()
            print("Would you like to add any other items to the catalog? (Y/N)")
            choice = input("\n>>> ")
            if choice in yes:
                t = False
            elif choice in no:
                t = True
            else:
                print("\nPlease select a valid option (Y - yes, N - no).")
                logging.info("Admin entered invalid input for binary (Y/N) selection...")
                continue
            break
        if t:
            break

    # start transaction
    cursor.execute("START TRANSACTION;")
    # build query from items list
    query = "INSERT INTO catalog (productName, type1, type2, salePrice, rentalPrice, stock) VALUES"
    for prod in items:
        query += f"('{prod.getName()}', '{prod.getType1()}', '{prod.getType2()}', {prod.getSalePrice()}, {prod.getRentalPrice()}, {prod.getStock()})"
        if prod.getId() == len(items)-1:
            query += ";"
        else:
            query += ", "
    # execute query
    cursor.execute(query)
    # commit changes
    cursor.execute("COMMIT;")

def addStock(cursor):
    clear()
    while True:
        print("What item are we adding stock to today? (Enter the product ID or enter 'q' to quit)")
        prod = input("\nProduct ID: ")
        if prod.lower() in {'q', 'quit'}:
            return
        if not prod.isnumeric():
            print("Please enter an appropriate product ID (must be an integer).")
            logging.info("Admin attempted to input non-integer for product ID...")
            continue
        id = int(prod)
        cursor.execute(f"SELECT productName, stock FROM catalog WHERE productID={id}")
        name, stock = None, None
        for record in cursor:
            if record is None:
                break
            name, stock = record[0], record[1]
        if name is None or stock is None:
            clear()
            print("Not a Valid Product ID. Please try again...")
            logging.info("Invalid Product ID entered...")
            continue
        while True:
            clear()
            print(f"Product ID: {id}, Product: {name}, Current Stock: {stock}")
            tf.pause(2)
            print("\nIs this the product with new stock? (Y/N)")
            choice = input("\n>>> ")
            if choice in yes:
                t = True
            elif choice in no:
                t = False
            else:
                print("\nPlease select a valid option (Y - yes, N - no).\n")
                logging.info("Invalid user input. Did not enter (Y/N) for binary question...")
                continue
            break
        if t:
            break
    while True:
        clear()
        print("How much of this product has been added to the inventory?")
        new_stock = input("\n>>> ")
        if not new_stock.isnumeric():
            print("Input must be an integer. Try again.")
            logging.info("Admin entered a non-integer for new inventory...")
            continue
        ns = int(new_stock)
        break
    # start transaction
    cursor.execute("START TRANSACTION;")
    cursor.execute(f"UPDATE catalog SET stock = {stock + ns} WHERE productid={id};")
    # commit changes
    cursor.execute("COMMIT;")
    logging.info(f"Updated inventory for {name} (Product ID: {id})...")

def adminTools(cursor, user):
    '''
    adminTools
    
    Gives user with admin permissions to admin features.
    
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
        print("---------- ADMINISTRATOR MENU ----------\n")
        print("\tView All Orders (1)")
        print("\tView All Items Sold (2)")
        print("\tView All Users (3)")
        print("\tView Inventory (4)")
        print("\tAdd to catalog (5)")
        print("\tAdd stock (6)")
        print("\tEdit Users (7)")
        print("\tExit to main menu (0)\n")
        choice = input("\nMake your selection: ")
        if choice.lower() in {"0", "q", "quit"}:
            clear()
            break
        elif choice == "1":
            # view all orders
            clear()
            print(f'{"ID".rjust(3)} | {"Username".ljust(20)} | Total     | Transaction Date/Time')
            query0 = 'WITH t1 AS (SELECT SUM(price) as tot_price, OrderID FROM itemsSold GROUP BY OrderID) SELECT t1.OrderID, username, tot_price, transactionTime FROM orders JOIN t1 ON t1.OrderID=orders.OrderID;'
            cursor.execute(query0)
            for record in cursor:
                price = '{:.2f}'.format(record[2])
                print(f'{str(record[0]).rjust(3)} | {record[1].ljust(20)} | ${price.rjust(8)} | {record[3]}')
            input("\nPress enter to continue.")
            logging.info("Admin viewed all orders...")
            clear()
        elif choice == "2":
            # view all items sold
            clear()
            print(f'Sale ID | Order ID | {"Product".ljust(25)} | ID  | Quantity')
            cursor.execute("SELECT UnitID, OrderID, productName, catalog.productID, quantity FROM itemsSold JOIN catalog ON itemsSold.productid=catalog.productid;")
            for record in cursor:
                print(f'{str(record[0]).rjust(7)} | {str(record[1]).rjust(8)} | {record[2].ljust(25)} | {str(record[3]).rjust(3)} | {record[4]}')
            input("\nPress enter to continue.")
            logging.info("Admin viewed all items sold...")
            clear()
        elif choice == "3":
            # view all users
            clear()
            print(f"{'Username'.ljust(26)}| {'Name'.ljust(29)}| {'Address'.ljust(40)}| Account Balance | Admin")
            cursor.execute("SELECT username, firstName, lastName, address, balance, adminAccess FROM customers;")
            for record in cursor:
                if record[5] == True:
                    ad_acc = 'Yes'
                else:
                    ad_acc = 'No'
                if record[4] is None:
                    bal = str(record[4]).ljust(15)
                else:
                    bal = f"${'{:.2f}'.format(record[4]).rjust(14)}"
                name = str(record[1]) + " " + str(record[2])
                print(f"{record[0].ljust(26)}| {name.ljust(29)}| {str(record[3]).ljust(40)}| {bal} | {ad_acc}")
            input("\nPress enter to continue.")
            logging.info("Admin viewed all users...")
        elif choice == "4":
            # view inventory
            clear()
            cursor.execute("SELECT ProductID, productName, stock FROM catalog;")
            logging.info("User accessed catalog table in project1 database...")

            print(f'ID  | {"Product Name".ljust(25)} | Inventory')
            print("|".rjust(5,"-") + "|".rjust(28,"-") + "".center(15,"-"))

            for record in cursor:
                print(f'{str(record[0]).zfill(3)} | {record[1].ljust(25)} | {record[2]}')
                print("|".rjust(5) + "|".rjust(28))
            
            input("\n\nPress Enter to exit catalog.")
        elif choice == "5":
            addItem(cursor)
        elif choice == "6":
            addStock(cursor)
        elif choice == "7":
            # edit user info
            while True:
                print("\nEnter the username for the user you want to edit:")
                e_usern = input("\n>>> ")
                if e_usern.lower() in {'q', 'quit'}:
                    break
                cursor.execute(f"SELECT firstName, lastName, address, passkey, balance, adminAccess FROM customers WHERE username='{e_usern}';")
                lst = cursor.fetchall()
                if lst == []:
                    print("Couldn't find user in records...")
                    logging.info("Couldn't find user in database...")
                    tf.pause(2)
                    continue
                else:
                    for record in lst:
                        e_user = User(e_usern, record[0], record[1], record[2], record[3], record[4], record[5])
                        editUser(cursor, e_user, True, user)
                        break
                break

        else:
            print("Please select a valid option (Enter a digit between 0 and 4).")
            input("\nPress enter to continue.")
    
def disableUser(cursor, user):
    '''
    disableUser
    
    Allows the user to disable their account from the database. Does not
    remove all data. Removes name, address, and balance. Keeps username
    and passkey for later reactivation. Admin accounts cannot be disabled
    without removing admin access.

    Returns True.

    '''
    clear()
    if user.isAdmin():
        print("Cannot disable admin account. Returning to menu...")
        tf.pause(2)
        logging.info("User attempted to disable account without removing admin privileges...")
        return
    # start transaction
    cursor.execute("START TRANSACTION;")
    cursor.execute(f"UPDATE customers SET firstName = 'DISABLED', lastName = NULL, address = NULL, balance = NULL WHERE username = '{user.getUsername()}';")
    user._fname = "DISABLED"
    user._lname = None
    user._address = None
    user._balance = None
    # commit changes
    cursor.execute("COMMIT;")
    print("Account successfully disabled.")

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

    # update balance to 0
    cursor.execute(f"UPDATE customers SET balance = 0 WHERE username='{username}'")

    user = User(username, fname, lname, address, nkey, 0)

    # commit changes
    cursor.execute("COMMIT;")

    return user

def formatAddress():
    '''
    formatAddress
    
    Prompts user input to properly format their address for their record in the database
    
    '''
    quit = {'q', 'quit'}
    print("\nAt any point, you may enter 'q' to quit.")
    print("Please enter your street address. Do not include city, state, or ZIP Code information.\n")
    street = input("\nAddress: ")
    if street.lower() in quit:
        return
    clear()
    print("Please enter your city.\n")
    city = input("\nCity: ").capitalize()
    if city.lower() in quit:
        return
    while True:
        clear()
        print("Please enter your state initials (e.g. New York = NY, Texas = TX, etc.).\n")
        try:
            st = input("\nState: ")
            if st.lower() in {'q', 'quit'}:
                return
            if len(st) > 2:
                raise Exception
            state = st[0].capitalize() + st[1].capitalize()
            break
        except Exception:
            clear()
            print("You must enter the initials of the state, not the full name.")
            continue
    while True:
        clear()
        print("Please enter your ZIP Code.\n")
        zip = input("\nZIP Code: ")
        if zip.lower() in quit:
            return
        if not zip.isnumeric():
            print("\nZIP code must only contain digits!")
        elif len(zip) != 5:
            print("\nZIP Code must be 5 digits long!")
        else:
            break
        tf.pause(2)
        logging.info("User entered invalid input for ZIP Code...")


    return f"{street}, {city}, {state} {zip}"

def changeName(cursor, user):
    '''
    changeName
    
    Prompts user input to change name in database.
    
    '''
    clear()
    # display current name in db
    cursor.execute(f"SELECT firstName, lastName FROM customers WHERE username='{user.getUsername()}';")
    for record in cursor:
        if record is None:
            print("Couldn't get name from database")
            logging.info("Unable to read data from database...")
            break
        else:
            print(f"Current Name: {record[0]} {record[1]}")

    print("\nPlease enter your first and last name. Please connect multiple last names using a dash (-). Enter 'q' to quit.")
    ninp_r = input("\nName: ")
    if ninp_r.lower() in {'q', 'quit'}:
        return
    ninp = ninp_r.split(" ")
    # start transaction
    cursor.execute("START TRANSACTION;")
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

def changePassword(cursor, user, user2=None):
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
        if user2 is None:
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
        else:
            user_key = user2.getPasskey()
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
            print("PASSWORD RULES".center(50,"*") + rules)
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

def editUser(cursor, user, admin=False, user2=None):
    '''
    editUser

    Gives user access to their account settings.
    '''
    while True:
        clear()
        if admin:
            print(f"User: {user.getUsername()}\n")
        print("Please select an option from below:\n")
        print("\tView Balance (1)")
        print("\tAdd To Balance (2)")
        print("\tChange Address (3)")
        print("\tChange Name (4)")
        print("\tChange Password (5)")
        print("\tDisable account (6)")
        if admin:
            if user.isAdmin():
                print("\tDemote User from Administrator (7)")
            else:
                print("\tPromote User to Administrator (7)")
        print("\tExit menu (0)")
        choice = input("\n>>> ")

        if choice == "0":
            return None
        elif choice == "1":
            # view balance
            clear()
            print(f"Your balance: ${'{:.2f}'.format(user.getBalance())}\n")
            tf.pause(1)
            input("\nPress enter to continue.\n")
        elif choice == "2":
            clear()
            curr_bal = user.getBalance()
            print(f"Your balance: ${'{:.2f}'.format(curr_bal)}\n")
            balance = user.addToBalance()
            # start transaction
            cursor.execute("START TRANSACTION;")
            cursor.execute(f"UPDATE customers SET balance = {balance} WHERE username = '{user.getUsername()}'")
            # commit changes
            cursor.execute("COMMIT;")
            clear()
            chng = balance - curr_bal
            print(f"Successfully added ${'{:.2f}'.format(chng)} to your account!")
            tf.pause(2)
        elif choice == "3":
            clear()
            # display current address
            cursor.execute(f"SELECT address FROM customers WHERE username = '{user.getUsername()}';")
            for record in cursor:
                if record is None:
                    print("Couldn't get current address...")
                    tf.pause(2)
                    break
                print(f"Current Address: {record[0]}")
            # change address
            new_address = formatAddress()
            if new_address is str:
                user.setAddress(new_address)
                # start transaction
                cursor.execute("START TRANSACTION;")
                cursor.execute(f"UPDATE customers SET address = '{user.getAddress()}' WHERE username='{user.getUsername()}';")
                logging.info("User updated address in database...")
                # commit changes
                cursor.execute("COMMIT;")
        elif choice == "4":
            changeName(cursor, user)
        elif choice == "5":
            changePassword(cursor, user, user2)
        elif choice == "6":
            if admin:
                pronoun = f"{user.getName(1)}'s"
                poss = pronoun + "'s"
                poss2 = "their"
            else:
                pronoun = "You"
                poss = "your"
                poss2 = poss
            print(f"\nAre you sure you want to disable {poss} account? This will remove personal data but\nwill not remove {poss} username or order history. {pronoun} can reactivate {poss2} account later.")
            disable_choice = input("\nY/N: ").lower()
            if disable_choice in yes:
                disableUser(cursor, user)
            elif disable_choice in no:
                continue
            else:
                print("\nInvalid input. Returning to previous menu...")
                tf.pause(2)
                logging.info("Invalid input. Returning to account settings menu...")
                continue
        elif choice == "7":
            if user.isAdmin():
                # demote from admin
                while True:
                    clear()
                    print(f"Are you sure you want to remove {user.getUsername()} as Administrator? (Y/N)")
                    a_choice = input("\n>>> ")
                    if a_choice in yes:
                        pcount = 0
                        while True:
                            print("\nPlease enter the admin password below.")
                            apass = getpass("\nPassword: ")
                            akey = passKeyGenerator(apass, cursor)
                            if pcount >= 5:
                                tf.pause(1)
                                print("5 Incorrect passsord attempts.")
                                tf.pause(1)
                                tf.slowPrint("\nExiting program", 0.02)
                                tf.pause(1)
                                tf.slowPrint("...", 0.5)
                                print()
                                logging.info("5 incorrect administrator password attempts. Exiting menu...")
                                break
                            elif akey != user2.getPasskey():
                                clear()
                                pcount += 1
                                print(f"Sorry, that password is incorrect. Please try again. {6 - pcount} attempt(s) remaining.\n")
                                continue
                            elif akey == user2.getPasskey():
                                clear()
                                # slow text and pauses gives admin opportunity to abort operation if necessary
                                tf.slowPrint(f"Removing User {user.getUsername()} from Administrator.", 0.01)
                                tf.slowPrint("...", 0.1)
                                tf.pause(1)
                                # start transaction
                                cursor.execute("START TRANSACTION;")
                                cursor.execute(f"UPDATE customers SET adminAccess = False WHERE username='{user.getUsername()}';")
                                # commit changes
                                cursor.execute("COMMIT;")
                                clear()
                                print(f"Operation completed successfully! {user.getUsername()} no longer has administrator privileges.")
                                logging.info(f"User {user.getUsername()} successfully removed as admin...")
                                tf.pause(2.5)
                            break
                        break
                    elif a_choice in no:
                        break
                    else:
                        print("Please select a valid option (Y - yes, N - no).")
                        logging.info("Admin entered invalid input for binary (Y/N) selection...")
                        continue
            else:
                # promote to admin
                while True:
                    clear()
                    print(f"Are you sure you want to promote {user.getUsername()} to Administrator? (Y/N)")
                    a_choice = input("\n>>> ")
                    if a_choice in yes:
                        pcount = 0
                        while True:
                            print("\nPlease enter the admin password below.")
                            apass = getpass("\nPassword: ")
                            akey = passKeyGenerator(apass, cursor)
                            if pcount >= 5:
                                tf.pause(1)
                                print("5 Incorrect passsord attempts.")
                                tf.pause(1)
                                tf.slowPrint("\nExiting program", 0.02)
                                tf.pause(1)
                                tf.slowPrint("...", 0.5)
                                print()
                                logging.info("5 incorrect administrator password attempts. Exiting menu...")
                                break
                            elif akey != user2.getPasskey():
                                clear()
                                pcount += 1
                                print(f"Sorry, that password is incorrect. Please try again. {6 - pcount} attempt(s) remaining.\n")
                                continue
                            elif akey == user2.getPasskey():
                                clear()
                                # slow text and pauses gives admin opportunity to abort operation if necessary
                                tf.slowPrint(f"Setting User {user.getUsername()} to Administrator.", 0.01)
                                tf.slowPrint("...", 0.1)
                                tf.pause(1)
                                # start transaction
                                cursor.execute("START TRANSACTION;")
                                cursor.execute(f"UPDATE customers SET adminAccess = True WHERE username='{user.getUsername()}';")
                                # commit changes
                                cursor.execute("COMMIT;")
                                clear()
                                print(f"Operation completed successfully! {user.getUsername()} now has administrator privileges.")
                                logging.info(f"User {user.getUsername()} successfully upgraded to admin...")
                                tf.pause(2.5)
                            break
                        break
                    elif a_choice in no:
                        break
                    else:
                        print("Please select a valid option (Y - yes, N - no).")
                        logging.info("Admin entered invalid input for binary (Y/N) selection...")
                        continue
        else:
            m_choice = 6
            if admin:
                m_choice = 7
            print(f"Please choose a valid option (Select a digit from 0-{m_choice}).")
            logging.info("User entered invalid input...")
            tf.pause(2)
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
    print("\tGeneral (6)")
    print("\tEntire catalog (0)")
    print("\nEnter any other input to return to previous menu.")
    choice2 = input("\n>>> ")

    if choice2 == "0":
        query += ";"
    else:
        if choice == "0":
            query += " WHERE type2="
        else:
            query += " AND type2="
        if choice2 == "1":
            query += "'Band'"
        elif choice2 == "2":
            query += "'Orchestra'"
        elif choice2 == "3":
            query += "'Percussion'"
        elif choice2 == "4":
            query += "'Electronics'"
        elif choice2 == "5":
            query += "'Rhythm'"
        elif choice2 == "6":
            query += "'General'"
        else:
            return False

    clear()
    cursor.execute(query)
    logging.info("User accessed catalog table in project1 database...")

    print(f'{"Product Name".ljust(25)}| ID  | Sale Price | {"Rental Price".ljust(15)}')
    print("|".rjust(26,"-") + "|".rjust(6,"-") + "|".rjust(13,"-") + "".center(15,"-"))

    for record in cursor:
        tf.pause(0.05)
        product = Product(record[0], record[1], record[2], record[3], record[4], record[5], record[6])
        print(product, "\n" + "|".rjust(26) + "|".rjust(6) + "|".rjust(13))
    
    tf.pause(2)
    input("\n\nPress Enter to exit catalog.")
    
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
            print()
            while True:
                print("Please enter your password.\n")
                # password = input("\nPassword: ")
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
                    logging.info("5 failed password attempts. Exiting program...")
                    return None
                if ckey != key:
                    clear()
                    pcount += 1
                    print(f"Sorry, that password is incorrect. Please try again. {6 - pcount} attempt(s) remaining.\n")
                    tf.pause(3)
                    clear()
                    continue
                elif ckey == key:
                    clear()
                    print("Login successful.")
                    tf.pause(1)
                    print(f"\nWelcome back, {_user[1]}!")
                    if _user[6] == True:
                        user = User(_user[0], _user[1], _user[2], _user[3], _user[4], _user[5], True)
                    else:
                        user = User(_user[0], _user[1], _user[2], _user[3], _user[4], _user[5])
                    logging.info(f"User {username} has logged into the application...")
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
    logging.info(f"New passkey generated...")
    return n1 * n2

def clear():
    os.system("cls")

if __name__ == "__main__":
    main()