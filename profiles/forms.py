from django import forms
from django.core.validators import FileExtensionValidator
from .models import Client, DigitalProfile, validate_about_video_size


class BusinessProfileForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        queryset=Client.objects.none(),
        label='Client',
    )
    google_maps_url = forms.URLField(
        label='Google Maps location URL',
        required=False,
        max_length=500,
        help_text='Paste a location link from Google Maps (open the location, choose Share, then Copy link).',
    )
    social_instagram = forms.URLField(label='Instagram profile URL', required=False)
    social_facebook = forms.URLField(label='Facebook profile URL', required=False)
    social_x = forms.URLField(label='X profile URL', required=False)
    social_youtube = forms.URLField(label='YouTube profile URL', required=False)
    social_tiktok = forms.URLField(label='TikTok profile URL', required=False)
    social_threads = forms.URLField(label='Threads profile URL', required=False)
    social_telegram = forms.URLField(label='Telegram profile URL', required=False)
    social_github = forms.URLField(label='GitHub profile URL', required=False)
    social_discord = forms.URLField(label='Discord profile URL', required=False)
    social_pinterest = forms.URLField(label='Pinterest profile URL', required=False)
    social_snapchat = forms.URLField(label='Snapchat profile URL', required=False)
    social_reddit = forms.URLField(label='Reddit profile URL', required=False)
    social_twitch = forms.URLField(label='Twitch profile URL', required=False)
    social_medium = forms.URLField(label='Medium profile URL', required=False)
    social_behance = forms.URLField(label='Behance profile URL', required=False)
    social_dribbble = forms.URLField(label='Dribbble profile URL', required=False)

    about_video = forms.FileField(
        label='About Me Video',
        required=False,
        help_text='Upload an MP4, WebM, or OGV video up to 50 MB. Use the clear checkbox to remove the current video.',
        validators=[
            FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'ogv']),
            validate_about_video_size,
        ],
    )

    class Meta:
        model = DigitalProfile
        fields = [
            'client',
            'unique_id',
            'slug',
            'color_theme',
            'first_name',
            'last_name',
            'display_name',
            'title',
            'department',
            'organization',
            'profile_photo',
            'about_video',
            'organization_logo',
            'phone',
            'email',
            'website',
            'address',
            'google_maps_url',
            'bio',
            'linkedin_url',
            'whatsapp_number',
            'social_instagram',
            'social_facebook',
            'social_x',
            'social_youtube',
            'social_tiktok',
            'social_threads',
            'social_telegram',
            'social_github',
            'social_discord',
            'social_pinterest',
            'social_snapchat',
            'social_reddit',
            'social_twitch',
            'social_medium',
            'social_behance',
            'social_dribbble',
            'is_active',
        ]

    SOCIAL_FIELDS = {
        'social_instagram': 'Instagram',
        'social_facebook': 'Facebook',
        'social_x': 'X',
        'social_youtube': 'YouTube',
        'social_tiktok': 'TikTok',
        'social_threads': 'Threads',
        'social_telegram': 'Telegram',
        'social_github': 'GitHub',
        'social_discord': 'Discord',
        'social_pinterest': 'Pinterest',
        'social_snapchat': 'Snapchat',
        'social_reddit': 'Reddit',
        'social_twitch': 'Twitch',
        'social_medium': 'Medium',
        'social_behance': 'Behance',
        'social_dribbble': 'Dribbble',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['color_theme'].required = False
        if self.instance.pk:
            self.fields.pop('client')
        else:
            self.fields['client'].queryset = Client.objects.order_by('display_name', 'first_name', 'last_name')
        saved_links = self.instance.social_links or {}
        for field_name, platform in self.SOCIAL_FIELDS.items():
            self.initial.setdefault(field_name, saved_links.get(platform, ''))

    def clean_color_theme(self):
        return (
            self.cleaned_data.get('color_theme')
            or self.instance.color_theme
            or DigitalProfile.ColorTheme.FOREST
        )

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.social_links = {
            platform: self.cleaned_data[field_name]
            for field_name, platform in self.SOCIAL_FIELDS.items()
            if self.cleaned_data.get(field_name)
        }
        if commit:
            profile.save()
            self.save_m2m()
        return profile