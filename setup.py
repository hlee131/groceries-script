"""Setsup secrets.txt"""
from getpass import getpass

with open('secrets.txt', 'w') as file:
    ZIP = input('What is your zipcode? ')
    EMAIL = input("What's your email? ")
    PASSWORD = getpass('What is your password for that email? ')
    TARGET = input('Who would you like to send updates to? ')

    file.write(f'{ZIP}\n')
    file.write(f'{EMAIL}\n')
    file.write(f'{PASSWORD}\n')
    file.write(f'{TARGET}\n')

print('Setup done!')