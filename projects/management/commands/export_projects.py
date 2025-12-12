# projects/management/commands/export_projects.py
import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from projects.models import Project, ProjectImage
from django.core.serializers.json import DjangoJSONEncoder

class Command(BaseCommand):
    help = 'Export all projects and their images to a JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='projects_export.json',
            help='Output JSON file path'
        )

    def handle(self, *args, **options):
        output_file = options['output']
        projects_data = []

        for project in Project.objects.all().prefetch_related('images'):
            # Get project data
            project_data = {
                'title': project.title,
                'description': project.description,
                'short_description': project.short_description,
                'demo_url': project.demo_url,
                'source_code_url': project.source_code_url,
                'technologies': project.technologies,
                'featured': project.featured,
                'display_order': project.display_order,
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat(),
                'images': []
            }

            # Add main project image path if exists
            if project.image:
                project_data['main_image'] = project.image.url if project.image else None

            # Add additional project images
            for img in project.images.all():
                project_data['images'].append({
                    'image': img.image.url if img.image else None,
                    'caption': img.caption,
                    'display_order': img.display_order
                })

            projects_data.append(project_data)

        # Write to JSON file
        with open(output_file, 'w') as f:
            json.dump(projects_data, f, indent=2, cls=DjangoJSONEncoder)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully exported {len(projects_data)} projects to {output_file}')
        )