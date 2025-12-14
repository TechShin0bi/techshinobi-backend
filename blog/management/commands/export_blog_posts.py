import json
from django.core.management.base import BaseCommand
from django.utils.timezone import localtime
from blog.models import BlogPost, Comment


class Command(BaseCommand):
    help = "Export blog posts and their comments to a JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="blog_export.json",
            help="Output JSON file name",
        )

    def handle(self, *args, **options):
        output_file = options["output"]
        data = []

        posts = BlogPost.objects.all()
        
        for post in posts:
            comments_qs = Comment.objects.filter(post=post, is_active=True)

            comments = [
                {
                    # "author": comment.author.username if comment.author else None,
                    "content": comment.content,
                    "created_at": localtime(comment.created_at).isoformat(),
                    "updated_at": localtime(comment.updated_at).isoformat(),
                    "is_active": comment.is_active,
                }
                for comment in comments_qs
            ]

            data.append(
                {
                    "title": post.title,
                    "content": post.content,
                    "image": post.image.url if post.image else None,
                    # "author": post.author.username if post.author else None,
                    "created_at": localtime(post.created_at).isoformat(),
                    "updated_at": localtime(post.updated_at).isoformat(),
                    "is_published": post.is_published,
                    "comments": comments,
                }
            )

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.stdout.write(
            self.style.SUCCESS(f"✅ Exported {len(data)} blog posts to {output_file}")
        )
