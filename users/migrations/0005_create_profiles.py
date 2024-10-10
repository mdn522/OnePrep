# Generated by Django 5.1.1 on 2024-10-03 05:14
from django.conf import settings
from django.db import migrations




def create_missing_profiles(apps, schema_editor):
    User = apps.get_model("users", "User")
    Profile = apps.get_model("users", "Profile")
    # create missing profile
    for user in User.objects.filter(profile=None).only('id', 'profile').order_by('id'):
        profile = Profile.objects.create(user=user)
        profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_profile'),
    ]

    operations = [
        migrations.RunPython(create_missing_profiles, reverse_code=migrations.RunPython.noop),
    ]
