# projects/management/commands/import_projects.py
import os
import json
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from projects.models import Project, ProjectImage

class Command(BaseCommand):
    help = 'Import projects from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--input',
            type=str,
            default='projects_export.json',
            help='Input JSON file path'
        )

    def handle(self, *args, **options):
        input_file = options['input']
        
        try:
            with open(input_file, 'r') as f:
                projects_data = json.load(f)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File {input_file} not found"))
            return
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR(f"Invalid JSON file: {input_file}"))
            return

        for project_data in projects_data:
            # Create or update project
            project, created = Project.objects.update_or_create(
                title=project_data['title'],
                defaults={
                    'description': project_data['description'],
                    'short_description': project_data['short_description'],
                    'demo_url': project_data['demo_url'],
                    'source_code_url': project_data['source_code_url'],
                    'technologies': project_data['technologies'],
                    'featured': project_data['featured'],
                    'display_order': project_data['display_order'],
                }
            )

            # Handle main image if it exists in the import
            if 'main_image' in project_data and project_data['main_image']:
                # In a real implementation, you might want to download the image from the URL
                # For now, we'll just store the URL in a text field if needed
                # You can implement file download logic here if required
                pass

            # Handle additional images
            if 'images' in project_data:
                # Clear existing images
                project.images.all().delete()
                
                for img_data in project_data['images']:
                    ProjectImage.objects.create(
                        project=project,
                        # In a real implementation, you would download the image here
                        # For now, we'll just store the URL in the image field
                        image=img_data.get('image', ''),
                        caption=img_data.get('caption', ''),
                        display_order=img_data.get('display_order', 0)
                    )

            action = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(f'{action} project: {project.title}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {len(projects_data)} projects from {input_file}')
        )