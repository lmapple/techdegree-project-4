#!/usr/bin/env python

import csv,re,datetime
from peewee import *

if __name__ == '__main__':

    with open("inventory.csv", newline='') as csvfile:
        invreader = csv.DictReader(csvfile, delimiter=',')
        inv_list = list(invreader)


        for item in inv_list:
            item['product_name'] = str(item['product_name'])
            item['product_quantity'] = int(item['product_quantity'])
            item['product_price'] = int(float(re.search(r'\d.\d{2}',item['product_price']).group())*100)
            item['date_updated'] = datetime.date(int(re.search(r'\d{4}',item['date_updated']).group()),
                                                 int(re.match(r'\d{1,2}',item['date_updated']).group()),
                                                 int(re.search(r'\/\d{1,2}',item['date_updated']).group()[1:])
                                                 )


    db = SqliteDatabase('inventory.db')


    class Product(Model):
        product_id = IntegerField(primary_key=True)
        #product_id = AutoField()
        product_name = CharField(max_length=255, unique=True)
        product_quantity = IntegerField(default=0)
        product_price = IntegerField(default=0)
        date_updated = DateField()

        class Meta:
            datebase = db

        #Use PeeWee's built in primary_key functionality for the product_id field,
        # so that each product will have an automatically generated unique identifier.

    db.connect()
    db.create_tables([Product], safe=True)

    def add_items():
        for item in inv_list:
            try:
            Product.create(product_name=item['product_name'],
                           product_quantity=item['product_quantity'],
                           product_price=item['product_price'],
                           date_updated=item['date_updated'])
            except IntegrityError:
                product_name = Product.get(product_name=item['product_name'])
                product_name.


