# Generated by Django 3.0.11 on 2020-11-28 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0018_auto_20191220_0920'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['-date_created']},
        ),
        migrations.AlterModelOptions(
            name='productattribute',
            options={'ordering': ['code']},
        ),
        migrations.AlterModelOptions(
            name='productattributevalue',
            options={'ordering': ['attribute__code']},
        ),
        migrations.AddField(
            model_name='productattribute',
            name='ordering',
            field=models.IntegerField(default=1000, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='productattributevalue',
            unique_together=set(),
        ),
    ]
