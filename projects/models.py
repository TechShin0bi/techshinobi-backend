from django.db import models
from utils.models import BaseModel

class Project(BaseModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='projects/img/', blank=True, null=True)
    demo_url = models.URLField(blank=True, null=True)
    source_code_url = models.URLField(blank=True, null=True)
    technologies = models.CharField(max_length=200, help_text="Comma-separated list of technologies")
    featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.short_description and self.description:
            self.short_description = self.description[:297] + '...' if len(self.description) > 300 else self.description
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['display_order']
        db_table = 'projects'

class ProjectImage(BaseModel):
    project = models.ForeignKey(Project, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='projects/images/')
    caption = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']
        db_table = 'project_images'
    
    def __str__(self):
        return f"Image for {self.project.title}"