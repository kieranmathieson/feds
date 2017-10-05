# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-22 14:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('businessareas', '0001_initial'),
        ('fieldsettings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvailableFieldSpecSettingDb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_name', models.TextField(default='', help_text='Machine name of this setting, e.g., quantity_min.', max_length=50)),
                ('field_setting_order', models.IntegerField(default=1, help_text='Order of the setting in the settings list for the field.')),
                ('field_setting_params', models.TextField(blank=True, default='{}', help_text='JSON parameters to initialize the field setting.')),
                ('field_setting', models.ForeignKey(help_text='A setting the field can have.', on_delete=django.db.models.deletion.CASCADE, to='fieldsettings.FieldSettingDb')),
            ],
        ),
        migrations.CreateModel(
            name='FieldSpecDb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Title of this field specification.', max_length=200)),
                ('machine_name', models.TextField(default='', help_text='Machine name of this field_spec, e.g., fld_spec_quantity.', max_length=50)),
                ('description', models.TextField(blank=True, help_text='Description of this field specification.')),
                ('field_type', models.CharField(choices=[('pk', 'Primary key'), ('fk', 'Foreign key'), ('text', 'Text'), ('zip', 'Zip code'), ('phone', 'Phone'), ('email', 'Email address'), ('date', 'Date'), ('choice', 'Choice from a list'), ('currency', 'Currency'), ('int', 'Integer')], help_text='Field type', max_length=10)),
                ('field_params', models.TextField(blank=True, default='{}', help_text='JSON parameters to describe field spec.')),
                ('available_field_settings', models.ManyToManyField(help_text='Settings that this field specification can have.', related_name='available_field_settings', through='fieldspecs.AvailableFieldSpecSettingDb', to='fieldsettings.FieldSettingDb')),
            ],
        ),
        migrations.CreateModel(
            name='NotionalTableMembershipDb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_name', models.TextField(default='', help_text='Machine name of this table field spec, e.g., cust_cname.', max_length=50)),
                ('field_order', models.IntegerField(help_text='Order of the field in the notional table.')),
                ('field_spec', models.ForeignKey(help_text='Field in notional table.', on_delete=django.db.models.deletion.CASCADE, to='fieldspecs.FieldSpecDb')),
                ('notional_table', models.ForeignKey(help_text='Notional table the field is in.', on_delete=django.db.models.deletion.CASCADE, to='businessareas.NotionalTableDb')),
            ],
        ),
        migrations.AddField(
            model_name='fieldspecdb',
            name='notional_tables',
            field=models.ManyToManyField(related_name='notional_tables', through='fieldspecs.NotionalTableMembershipDb', to='businessareas.NotionalTableDb'),
        ),
        migrations.AddField(
            model_name='availablefieldspecsettingdb',
            name='field_spec',
            field=models.ForeignKey(help_text='Field that can have the setting.', on_delete=django.db.models.deletion.CASCADE, to='fieldspecs.FieldSpecDb'),
        ),
    ]