from django.db import migrations, models
import django.core.validators
import profiles.models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='digitalprofile',
            name='about_video',
            field=models.FileField(
                blank=True,
                upload_to='profile_videos/',
                validators=[
                    django.core.validators.FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'ogv']),
                    profiles.models.validate_about_video_size,
                ],
            ),
        ),
    ]