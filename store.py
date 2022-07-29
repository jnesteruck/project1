import mysql.connector
import mysql_config as c
import json
import re
import logging
from product import Product

def main():

    logging.basicConfig(filename="store.log", level=logging.DEBUG, format='%(asctime)s :: %(message)s')
    
    #print(passKeyGenerator("admin"))
    
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

    # user = login(cursor)
    viewCatalog(cursor)
    # viewOrderHistory(cursor, user)

def addOrder():
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

def addUser():
    '''
    addUser()


    '''
    pass

def editUser():
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
        user = input("\nUsername: ")
        query = 'SELECT passkey FROM customers WHERE username = "' + user + '";'
        cursor.execute(query)
        key = cursor
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