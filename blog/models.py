from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from ckeditor.fields import RichTextField
from utils.models import BaseModel

User = get_user_model()

class BlogPost(BaseModel):
    title = models.CharField(max_length=200)
    content = RichTextField()
    image = models.ImageField(upload_to='blog/images/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        db_table = 'blog_posts'




class Comment(BaseModel):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments' , blank=True, null=True)
    content = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'blog_comments'
    
    def __str__(self):
        return f'Comment by {self.author} on {self.post}'