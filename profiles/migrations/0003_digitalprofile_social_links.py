from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_digitalprofile_about_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='digitalprofile',
            name='social_links',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]