import random
import mysql.connector

conn = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "2001",
    #database = "cards"
)
cur = conn.cursor()

cur.execute("CREATE DATABASE IF NOT EXISTS mybank")
cur.execute("CREATE TABLE IF NOT EXISTS mybank.card (id INT PRIMARY KEY AUTO_INCREMENT, card_number TEXT, card_pin TEXT, balance INTEGER DEFAULT 0)")
conn.commit()






def start():
    while True:
        print("""\n1. Creat an account \n2. Log into account \n0. Exit\n""")

        try:
            user_start = int(input())
            if user_start == 1:
                CreatAccount()
            elif user_start == 2:
                LogIn()
            elif user_start == 0:
                conn.close()
                print("Bye!")
                exit()
                # break
            else:
                print("Invalid input")
        except ValueError:
            print("Invalid input")
            
    

def CreatAccount():
    global account
    global base_number
    base_number = "400000"
    card_pin = ""

    for a in range(9):
        base_number += str(random.randint(0, 9))

    checksum(validate_card(base_number), base_number)
    for b in range(4):
        card_pin += str(random.randint(0, 9))
    cur.execute("INSERT INTO mybank.card (card_number, card_pin) VALUES (%s, %s)", (card_number, card_pin))
    conn.commit()
    print(f"""\nYour card has been created \ncard number: {card_number} \ncard PIN: {card_pin}\n""")
    


def validate_card(base_number):

    contral = 0
    for i in range(len(base_number)):
        if (i + 1) % 2 != 0:
            digit = int(base_number[i]) * 2 
            if digit > 9:
                digit -= 9
        else:
            digit = int(base_number[i]) 
        contral += digit
    return contral
    

def checksum(contral, base_number):
    global card_number
    if (contral % 10) != 0:
        key_digit = (((contral // 10) + 1) * 10) - contral
    else:
        key_digit = 0
    card_number = f'{(base_number)}{str(key_digit)}'
    return card_number



def luhncheck(num):
    check = int(str(num)[-1])
    num_list = [int(x) for x in str(num)[0:15]]
    for i in range(len(num_list)):
        if (i + 1) % 2 == 1:
            num_list[i] *= 2
        if num_list[i] > 9:
            num_list[i] -= 9
    luhn = (sum(num_list) + check)
    if luhn % 10 == 0:
        return True
    else:
        return False

def LogIn():

    user_card = input("Enter card Number\n")
    cur.execute("SELECT card_number, card_pin FROM mybank.card WHERE card_number = %s", (user_card,))
    record = cur.fetchall() 
    if (bool(record)):
        if(user_card == record[0][0]):
            user_pin = input("Enter you PIN: \n")
            if(user_pin == record[0][1]):
                print("\nYou have successfully logged in!")
                account_management(user_card)
            else:
                print("\nWrong Pin")
                LogIn()
    else:
        print("\nUser does not exists")
        TryAgain(LogIn)
    
    return user_card



def TryAgain(function_name):
    try:
        que = int(input("\n1. Try Again \n2. Back to Main Menu\n"))
        if que == 1:
            function_name()
        elif que == 2:
            start()
        else:
            print("Invalid Input")
    except ValueError:
        print("Invalid Input")
        TryAgain(LogIn)


def transfer(user_card_num):
    recipient_card = input("Enter card number of recipient: \n")

    cur.execute("SELECT card_number FROM mybank.card")
    cardNumbers = cur.fetchall()
    for x in cardNumbers:
        if recipient_card == x[0]:
            if luhncheck(recipient_card) == True:
                if (user_card_num == recipient_card):
                    print("You can't transfer money to the same account!")
                    account_management(user_card_num)
                    return
                else:
                    cur.execute("SELECT balance FROM mybank.card WHERE card_number = %s", (user_card_num,))
                    balance = cur.fetchall()
                    sending_money = int(input("Enter how much money you want to transfer: \n"))
                    if (sending_money > balance[0][0]):
                        print("Not enough money!")
                        account_management(user_card_num)
                        return
                    elif sending_money == 0:
                        print("You can't transfer 0 to an account!!")
                        account_management(user_card_num)
                        return
                    else:
                        cur.execute("UPDATE mybank.card SET balance = balance - %s WHERE card_number = %s",(sending_money, user_card_num))
                        cur.execute("UPDATE mybank.card SET balance = balance + %s WHERE card_number = %s", (sending_money, recipient_card))
                        cur.execute("SELECT balance FROM mybank.card WHERE card_number = %s", (user_card_num,))
                        balance = cur.fetchall()
                        conn.commit()
                        print("success!")
                        print(f'Your Balance is: {balance[0][0]}')
                        account_management(user_card_num)
                        return
            else:
                print("Probably you made a mistake in the card number.")
                account_management(user_card_num)
                return
    
    print("Such a card does not exist.")


def accountBalance(user_card_num):
    cur.execute("SELECT balance FROM mybank.card WHERE card_number = %s", (user_card_num,))
    balance = cur.fetchall()
    print(f'\nBalance: {balance[0][0]} \n')

def addincome(user_card_num):
    user_income = int(input("Enter income: "))
    cur.execute("UPDATE mybank.card SET balance = balance + %s WHERE card_number = %s", (user_income, user_card_num))
    cur.execute("SELECT balance FROM mybank.card WHERE card_number = %s", (user_card_num,))
    balance = cur.fetchall()
    conn.commit()
    print("Income was added!")
    print(f'New Balance: {balance[0][0]}')

def closeAccount(user_card_num):
    pin = input("Enter the card pin: \n")
    cur.execute("SELECT card_number, card_pin FROM mybank.card WHERE card_number = %s", (user_card_num, ))
    records = cur.fetchall()
    if (pin == records[0][1]):
        cur.execute("DELETE FROM mybank.card WHERE card_number = %s AND card_pin = %s",(user_card_num, pin))
        conn.commit()
        print("The account has been closed!")
    else:
        print("Wrong PIN")
        account_management(user_card_num)

    


def account_management(user_card):
    print("""\n1. Balance \n2. Add income \n3. Do transfer \n4. Close account \n5. Log out \n0. Exit""")
    user_balance_logout = int(input())

    if user_balance_logout == 1:
        accountBalance(user_card)
        account_management(user_card)
    elif user_balance_logout == 2:
        addincome(user_card)
        account_management(user_card)
    elif user_balance_logout == 3:
        transfer(user_card)
        account_management(user_card)
    elif user_balance_logout == 4:
        closeAccount(user_card)
        start()      
    elif user_balance_logout == 5:
        print("You have succefully logout! \n")
        start()
    elif user_balance_logout == 0:
        conn.close()
        print("Bye!")
        exit()


start()

















