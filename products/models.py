# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
from django.db import models


class Brand(models.Model):
    brand_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'brand'


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'category'


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.CharField(unique=True, max_length=100)
    phone = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'customer'


class Ordertable(models.Model):
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, models.DO_NOTHING, blank=True, null=True)
    order_date = models.DateTimeField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'ordertable'


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    brand = models.ForeignKey(Brand, models.DO_NOTHING, blank=True, null=True)
    category = models.ForeignKey(Category, models.DO_NOTHING, blank=True, null=True)
    subcategory = models.ForeignKey('Subcategory', models.DO_NOTHING, blank=True, null=True)
    market_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, blank=True, null=True)
    stock_level = models.IntegerField()
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product'


class Orderitem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey('Ordertable', models.DO_NOTHING, blank=True, null=True)
    product = models.ForeignKey(Product, models.DO_NOTHING, blank=True, null=True)
    quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'orderitem'


class Subcategory(models.Model):
    subcategory_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'subcategory'
        unique_together = (('name', 'category'),)


class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'supplier'
