import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone
from django.db import transaction
from cms_app.models import (
    Page, BlogCategory, BlogPost, BlogComment,
    MediaItem, SiteConfiguration, Announcement
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Import dummy data for cms_app manual testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dir',
            default='cms_app/cms_app_manual_test_dummy_data',
            help='Directory containing the CSV files'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing'
        )

    def handle(self, *args, **options):
        directory = options['dir']
        clear_data = options['clear']
        
        # Check if directory exists
        if not os.path.exists(directory):
            self.stdout.write(self.style.ERROR(f'Directory {directory} does not exist'))
            return
        
        # Clear existing data if requested
        if clear_data:
            self.clear_existing_data()
        
        # Import data
        with transaction.atomic():
            self.import_blog_categories(os.path.join(directory, 'blog_categories.csv'))
            self.import_pages(os.path.join(directory, 'pages.csv'))
            self.import_blog_posts(os.path.join(directory, 'blog_posts.csv'))
            self.import_blog_comments(os.path.join(directory, 'blog_comments.csv'))
            self.import_announcements(os.path.join(directory, 'announcements.csv'))
        
        self.stdout.write(self.style.SUCCESS('Successfully imported cms_app dummy data'))

    def clear_existing_data(self):
        """Clear existing data"""
        self.stdout.write('Clearing existing data...')
        BlogComment.objects.all().delete()
        BlogPost.objects.all().delete()
        BlogCategory.objects.all().delete()
        Page.objects.all().delete()
        Announcement.objects.all().delete()
        # Don't delete MediaItem as they might be used by other apps
        # Don't delete SiteConfiguration as it's a singleton
        self.stdout.write(self.style.SUCCESS('Existing data cleared'))

    def import_blog_categories(self, file_path):
        """Import blog categories from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping blog categories import'))
            return
        
        self.stdout.write(f'Importing blog categories from {file_path}...')
        count = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                BlogCategory.objects.update_or_create(
                    slug=row['slug'],
                    defaults={
                        'name': row['name'],
                        'description': row['description'],
                    }
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} blog categories'))

    def import_pages(self, file_path):
        """Import pages from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping pages import'))
            return
        
        self.stdout.write(f'Importing pages from {file_path}...')
        count = 0
        
        # Get admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.WARNING('No admin user found, using first staff user'))
            admin_user = User.objects.filter(is_staff=True).first()
            if not admin_user:
                self.stdout.write(self.style.ERROR('No admin or staff user found, pages will not have a creator'))
                return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Page.objects.update_or_create(
                    slug=row['slug'],
                    defaults={
                        'title': row['title'],
                        'content': row['content'],
                        'meta_description': row['meta_description'],
                        'meta_keywords': row['meta_keywords'],
                        'status': row['status'],
                        'created_by': admin_user,
                        'updated_by': admin_user,
                    }
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} pages'))

    def import_blog_posts(self, file_path):
        """Import blog posts from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping blog posts import'))
            return
        
        self.stdout.write(f'Importing blog posts from {file_path}...')
        count = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Get author
                try:
                    author = User.objects.get(email=row['author_email'])
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'User with email {row["author_email"]} not found, skipping blog post'))
                    continue
                
                # Create or update blog post
                post, created = BlogPost.objects.update_or_create(
                    slug=row['slug'],
                    defaults={
                        'title': row['title'],
                        'content': row['content'],
                        'excerpt': row['excerpt'],
                        'meta_description': row['meta_description'],
                        'meta_keywords': row['meta_keywords'],
                        'status': row['status'],
                        'is_featured': row['is_featured'].lower() == 'true',
                        'allow_comments': row['allow_comments'].lower() == 'true',
                        'author': author,
                    }
                )
                
                # Set published_at if status is published
                if post.status == 'published' and not post.published_at:
                    post.published_at = timezone.now()
                    post.save()
                
                # Add categories
                if row['categories']:
                    categories = row['categories'].split(',')
                    for category_slug in categories:
                        try:
                            category = BlogCategory.objects.get(slug=category_slug.strip())
                            post.categories.add(category)
                        except BlogCategory.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f'Category with slug {category_slug} not found'))
                
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} blog posts'))

    def import_blog_comments(self, file_path):
        """Import blog comments from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping blog comments import'))
            return
        
        self.stdout.write(f'Importing blog comments from {file_path}...')
        count = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Get blog post
                try:
                    post = BlogPost.objects.get(slug=row['post_slug'])
                except BlogPost.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Blog post with slug {row["post_slug"]} not found, skipping comment'))
                    continue
                
                # Get author
                try:
                    author = User.objects.get(email=row['author_email'])
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'User with email {row["author_email"]} not found, skipping comment'))
                    continue
                
                # Create comment
                BlogComment.objects.create(
                    blog_post=post,
                    author=author,
                    content=row['content'],
                    status=row['status'],
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} blog comments'))

    def import_announcements(self, file_path):
        """Import announcements from CSV"""
        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f'File {file_path} does not exist, skipping announcements import'))
            return
        
        self.stdout.write(f'Importing announcements from {file_path}...')
        count = 0
        
        # Get admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.WARNING('No admin user found, using first staff user'))
            admin_user = User.objects.filter(is_staff=True).first()
            if not admin_user:
                self.stdout.write(self.style.ERROR('No admin or staff user found, announcements will not have a creator'))
                return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse dates
                start_date = timezone.now()
                end_date = None
                if row['end_date']:
                    try:
                        end_date = timezone.datetime.strptime(row['end_date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
                    except ValueError:
                        self.stdout.write(self.style.WARNING(f'Invalid end_date format for announcement {row["title"]}, using None'))
                
                # Create announcement
                Announcement.objects.create(
                    title=row['title'],
                    content=row['content'],
                    announcement_type=row['announcement_type'],
                    is_active=row['is_active'].lower() == 'true',
                    start_date=start_date,
                    end_date=end_date,
                    created_by=admin_user,
                )
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} announcements'))
