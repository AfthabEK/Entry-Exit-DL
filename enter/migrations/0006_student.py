# Generated by Django 4.2.3 on 2023-09-26 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enter', '0005_auto_20230127_0334'),
    ]

    operations = [
        migrations.CreateModel(
            name='student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rollno', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
    ]
