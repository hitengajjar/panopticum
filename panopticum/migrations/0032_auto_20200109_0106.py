# Generated by Django 2.1 on 2020-01-08 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panopticum', '0031_auto_20200108_1808'),
    ]

    operations = [
        migrations.AddField(
            model_name='componentversionmodel',
            name='meta_searchstr_locations',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='componentversionmodel',
            name='meta_searchstr_product_versions',
            field=models.TextField(blank=True),
        ),
    ]
