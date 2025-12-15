import os
import json
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from django.contrib.auth import get_user_model
from blog.models import BlogPost, Comment
from datetime import datetime

User = get_user_model()

class Command(BaseCommand):
    help = 'Import blog posts from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            'input_file',
            type=str,
            help='Input JSON file path containing blog posts data'
        )

    def handle(self, *args, **options):
        input_file = options['input_file']
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                blog_data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File {input_file} not found'))
            return
        
        # Get or create admin user
        try:
            # Try to get the first superuser
            author = User.objects.filter(is_superuser=True).first()
            # If no superuser exists, create one
            if not author:
                author = User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='adminpass123'  # In production, use a secure password
                )
                self.stdout.write(self.style.SUCCESS('Created default admin user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting/creating admin user: {str(e)}'))
            return
        
        created_count = 0
        updated_count = 0
        
        for post_data in blog_data:
            # Create or update the blog post with the admin user as author
            try:
                post, created = BlogPost.objects.update_or_create(
                    title=post_data['title'],
                    defaults={
                        'content': post_data['content'],
                        'author': author,  # Use the admin user as author
                        'is_published': post_data.get('is_published', True),
                        'created_at': datetime.fromisoformat(post_data['created_at']),
                        'updated_at': datetime.fromisoformat(post_data['updated_at']),
                    }
                )
                
                # Handle image if it exists
                if post_data.get('image'):
                    try:
                        # This assumes the image files are in the media directory
                        image_path = os.path.join(settings.MEDIA_ROOT, post_data['image'])
                        if os.path.exists(image_path):
                            with open(image_path, 'rb') as img_file:
                                post.image.save(
                                    os.path.basename(post_data['image']),
                                    File(img_file),
                                    save=False
                                )
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(
                            f"Error importing image {post_data.get('image')}: {str(e)}"
                        ))
                
                # Save the post to update any changes (like the image)
                post.save()
                
                # Import comments if they exist
                for comment_data in post_data.get('comments', []):
                    try:
                        Comment.objects.update_or_create(
                            post=post,
                            author=author,  # Use admin as comment author
                            content=comment_data['content'],
                            defaults={
                                'is_active': comment_data.get('is_active', True),
                                'created_at': datetime.fromisoformat(comment_data['created_at']),
                                'updated_at': datetime.fromisoformat(comment_data['updated_at']),
                            }
                        )
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(
                            f"Error creating comment: {str(e)}"
                        ))
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Error processing post '{post_data.get('title')}': {str(e)}"
                ))
                continue
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully processed {len(blog_data)} blog posts. '
            f'Created: {created_count}, Updated: {updated_count}'
        ))