# Generated by Django 4.2.7 on 2023-12-10 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('CustomerID', models.AutoField(primary_key=True, serialize=False)),
                ('Name', models.CharField(max_length=100)),
                ('BillingAddressL1', models.CharField(max_length=255)),
                ('BillingAddressL2', models.CharField(max_length=255)),
                ('Zipcode', models.CharField(max_length=10)),
                ('Email', models.EmailField(max_length=254)),
                ('PhoneNumber', models.CharField(max_length=15)),
            ],
        ),
    ]