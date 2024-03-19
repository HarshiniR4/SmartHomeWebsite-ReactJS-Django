# Generated by Django 4.2.7 on 2023-12-15 00:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shems_app', '0006_alter_devicehistory_timestamp'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=40)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shems_app.customer')),
            ],
        ),
    ]
