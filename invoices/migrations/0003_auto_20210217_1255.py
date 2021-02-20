# Generated by Django 3.1.6 on 2021-02-17 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0002_invoices_out_emission_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoices_out',
            name='receiver_name',
            field=models.CharField(default='ok', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='invoices_out',
            name='receiver',
            field=models.CharField(max_length=100),
        ),
    ]