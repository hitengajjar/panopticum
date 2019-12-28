# Generated by Django 2.1 on 2019-12-27 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panopticum', '0010_auto_20191227_0227'),
    ]

    operations = [
        migrations.AddField(
            model_name='componentversionmodel',
            name='meta_mt_rating',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='componentversionmodel',
            name='meta_op_rating',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='componentversionmodel',
            name='meta_profile_completion',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='componentversionmodel',
            name='meta_qa_rating',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='componentversionmodel',
            name='meta_rating',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='componentversionmodel',
            name='mt_applicable',
            field=models.BooleanField(default=True, help_text='Maintainability requirements applicable?'),
        ),
        migrations.AddField(
            model_name='componentversionmodel',
            name='op_applicable',
            field=models.BooleanField(default=True, help_text='Operational requirements applicable?'),
        ),
        migrations.AddField(
            model_name='componentversionmodel',
            name='qa_applicable',
            field=models.BooleanField(default=True, help_text='Tests requirements applicable?'),
        ),
    ]