# Generated by Django 4.0.4 on 2022-05-02 07:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('itineraires', '0007_alter_comment_pub_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images/')),
                ('trip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='itineraires.sortie', verbose_name='Sortie')),
            ],
        ),
    ]
