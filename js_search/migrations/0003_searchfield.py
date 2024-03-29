# Generated by Django 2.2.10 on 2020-05-13 11:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        #('cms', '0022_auto_20180620_1551'),
        ('js_search', '0002_searchextension'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchField',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='js_search_searchfield', serialize=False, to='cms.CMSPlugin')),
                ('title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Title')),
                ('results_type', models.CharField(blank=True, default='', max_length=255, verbose_name='Results')),
                ('layout', models.CharField(blank=True, default='', max_length=60, verbose_name='layout')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
