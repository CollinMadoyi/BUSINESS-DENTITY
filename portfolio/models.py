from django.db import models
from profiles.models import Client

class PortfolioProfile(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='portfolio_profiles')
    about = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    education = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    achievements = models.TextField(blank=True)

    def __str__(self):
        return self.client.display_name

class PortfolioProject(models.Model):
    portfolio = models.ForeignKey(PortfolioProfile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='portfolio/projects/', blank=True, null=True)
    technologies = models.TextField(blank=True)
    project_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title
