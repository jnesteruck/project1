import mysql.connector
import mysql_config as c
import json
import re
import logging

def main():
    
    print(passKeyGenerator("jacob01"))

    # login()
    
    # try:
    #     cnx = mysql.connector.connect(user=c.user, password=c.password, host=c.host, database = "project1")
    #     cursor = cnx.cursor()
    # except mysql.connector.Error as mce:
    #     print(mce.msg)
    #     logging.info("Database error occurred. Exiting program...")
    #     return
    # except Exception as e:
    #     print("ERROR: Exiting program...")
    #     logging.info("Fatal error occurred. Exiting program...")
    #     return

    # logging.basicConfig(filename="store.log", level=logging.DEBUG, format='%(asctime)s :: %(message)s')

def addOrder():
    '''
    addOrder


    '''
    pass

def createOrderHistory():
    '''
    createOrderHistory


    '''
    pass

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

def viewCatalog():
    '''
    viewCatalog


    '''
    pass

def login():
    '''
    login


    '''
    print("\nPlease enter your username:\n")
    user = input("\nUsername: ")

    pass

def searchKeyFile(char):
    with open("passKey.csv", "r") as f:
            for line in f:
                idx = int(line.split(",")[0])
                string = line.split(",")[1]
                print(idx)
                if re.search(f'{char}', string):
                    print("found", char, "at index", idx)
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
    print(password)
    for char in p1:
        print(char)
        n1 += searchKeyFile(char)
    for char in p2:
        print(char)
        n2 += searchKeyFile(char)
    return n1 * n2


    
if __name__ == "__main__":
    main()