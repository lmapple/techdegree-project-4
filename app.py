#!/usr/bin/env python

import csv,re,datetime
from peewee import *


#Read csv file and create a list of dictionaries
with open("inventory.csv", newline='') as csvfile:
    invreader = csv.DictReader(csvfile, delimiter=',')
    inv_list = list(invreader)

#Format data in list
    for item in inv_list:
        item['product_name'] = str(item['product_name'])
        item['product_quantity'] = int(item['product_quantity'])
        item['product_price'] = int(float(re.search(r'\d.\d{2}',item['product_price']).group())*100)
        item['date_updated'] = datetime.date(int(re.search(r'\d{4}',item['date_updated']).group()),
                                             int(re.match(r'\d{1,2}',item['date_updated']).group()),
                                             int(re.search(r'\/\d{1,2}',item['date_updated']).group()[1:])
                                             )

#Initialize database
db = SqliteDatabase('inventory.db')

#Create Product model with five attributes
class Product(Model):
    product_id = IntegerField(primary_key=True)
    product_name = CharField(max_length=255, unique=True)
    product_quantity = IntegerField(default=0)
    product_price = IntegerField(default=0)
    date_updated = DateField()

    class Meta:
        database = db

if __name__ == '__main__':

#Connect to the database and create tables
    db.connect()
    db.create_tables([Product], safe=True)

#Function to add data from csv file into database
    def add_items_from_csv():
        for item in inv_list:
            try:
                Product.create(product_name=item['product_name'],
                               product_quantity=item['product_quantity'],
                               product_price=item['product_price'],
                               date_updated=item['date_updated'])
            except IntegrityError:
                product_record = Product.get(product_name=item['product_name'])

#Check to make sure old data does not overwrite more recent data in the database
                if product_record.date_updated < item['date_updated']:
                    product_record.product_quantity = item['product_quantity']
                    product_record.product_price = item['product_price']
                    product_record.date_updated = item['date_updated']
                    product_record.save()
                else:
                    pass

#Function to manage user menu and input
    def user_menu():
        while True:
            user_input = input("(V)iew details of a product, (A)dd a new product, Create a (b)ackup of the database, "+
                               "(Q)uit\n")

            if user_input.upper() == 'V':
                display_product()

            elif user_input.upper() == 'A':
                add_single_item()

            elif user_input.upper() == 'B':
                create_backup()

            elif user_input.upper() == 'Q':
                print("Goodbye.")
                break
            else:
                print("Invalid option. Please try again.")

#Function to display individual product
    def display_product():
        while True:
            product_id_from_user = input("Please enter the product id number of the product you would like " +
                                         "to view.\n")
            try:
                product_record = Product.get(product_id=product_id_from_user)
                print("\nProduct ID: " + str(product_record.product_id) +
                      "\nProduct Name: " + str(product_record.product_name) +
                      "\nProduct Quantity: " + str(product_record.product_quantity) +
                      "\nProduct Price: " + "$" + str(product_record.product_price / 100) +
                      "\nDate Updated: " + str(product_record.date_updated) +
                      "\n")
                break
            except ValueError:
                print("Invalid product id. Please try again. The valid range is from " +
                      str(Product.select().order_by(Product.product_id.asc()).get()) + " to " +
                      str(Product.select().order_by(Product.product_id.desc()).get()) + ".")
            except DoesNotExist:
                print("Invalid product id. Please try again. The valid range is from " +
                      str(Product.select().order_by(Product.product_id.asc()).get()) + " to " +
                      str(Product.select().order_by(Product.product_id.desc()).get()) + ".")

#Function to add a new product. If product already exists and the entered data is more recent
#than the existing, product information will be updated
    def add_single_item():
        try:
            while True:
                product_name = str(input("What is the name of the product you want to add?\n"))
                if product_name != "":
                    break
            while True:
                product_quantity = int(input("What is the quantity of the product?\n"))
                if product_quantity >= 0:
                    break
                else:
                    print("Quantity cannot be less than zero.")
            while True:
                product_price = int(float(input("What is the price of the product?\n"))*100)
                if product_price >= 0:
                    break
                else:
                    print("Price cannot be less than zero.")
            date_updated = datetime.date.today()

            try:
                Product.create(product_name=product_name,
                               product_quantity=product_quantity,
                               product_price=product_price,
                               date_updated=date_updated)
            except IntegrityError:
                product_record = Product.get(product_name=product_name)

#Check to make sure old data does not overwrite more recent data in the database
                if product_record.date_updated <= date_updated:
                    product_record.product_quantity = product_quantity
                    product_record.product_price = product_price
                    product_record.date_updated = date_updated
                    product_record.save()
                else:
                    print("Duplicate product found. Existing data is more current. Product not modified.")
        except ValueError:
            print("Invalid value. Item not added.")

#Function to create a csv backup of the database
    def create_backup():
        with open('backup.csv','w') as csvfile:
            fieldnames = ['product_id','product_name','product_quantity','product_price','date_updated']
            backupwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)

            backupwriter.writeheader()
            product_data = Product.select().dicts()

            for product_record in product_data:
                backupwriter.writerow({
                    'product_id': product_record['product_id'],
                    'product_name': product_record['product_name'],
                    'product_quantity': product_record['product_quantity'],
                    'product_price': product_record['product_price'],
                    'date_updated': product_record['date_updated'],
                })
        print("Backup created.")

#Update the database and run the user menu
    user_input = input("Welcome to your Store Inventory Menu. Would you like to update your database to match "
                       + "your current csv file?\n(Y)es or (N)o?\n")
    if user_input.upper() == 'Y':
        add_items_from_csv()
        print("Database updated. What would you like to do now?")
    else:
        print("Database not updated. What would you like to do now?")
    user_menu()
    db.close()