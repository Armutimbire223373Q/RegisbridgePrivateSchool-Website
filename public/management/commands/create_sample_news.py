from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from public.models import NewsPost
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = "Create sample news posts for testing"

    def handle(self, *args, **options):
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username="testuser",
            defaults={
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User",
                "is_staff": True,
            },
        )

        if created:
            user.set_password("testpass123")
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created test user: {user.username}"))

        # Sample news data
        sample_news = [
            {
                "title": "Welcome to Regisbridge College",
                "excerpt": "A warm welcome to all new and returning students for the academic year.",
                "content": "We are excited to welcome all students back to Regisbridge College for another promising academic year. Our dedicated staff is committed to providing quality education and fostering a supportive learning environment.",
                "category": "announcements",
                "is_published": True,
            },
            {
                "title": "Annual Sports Day Announced",
                "excerpt": "Mark your calendars for our annual sports day celebration.",
                "content": "The annual sports day will be held on October 15th, featuring various athletic competitions, team sports, and fun activities for all students. Parents are welcome to attend and cheer on their children.",
                "category": "events",
                "is_published": True,
            },
            {
                "title": "New Science Lab Equipment",
                "excerpt": "Our science department has received state-of-the-art laboratory equipment.",
                "content": "Thanks to generous donations, our science department now features modern laboratory equipment that will enhance students' learning experience in physics, chemistry, and biology.",
                "category": "academic",
                "is_published": True,
            },
            {
                "title": "Art Exhibition Success",
                "excerpt": "Student artwork showcased in successful annual exhibition.",
                "content": "Our annual art exhibition was a tremendous success, showcasing the creative talents of our students. The event attracted visitors from the community and highlighted the importance of arts in education.",
                "category": "arts",
                "is_published": True,
            },
            {
                "title": "Community Service Initiative",
                "excerpt": "Students participate in local community service projects.",
                "content": "Our students have been actively involved in various community service projects, including environmental cleanup, visiting elderly homes, and supporting local charities. These initiatives help develop social responsibility.",
                "category": "community",
                "is_published": True,
            },
        ]

        created_count = 0
        for news_data in sample_news:
            news_post, created = NewsPost.objects.get_or_create(
                title=news_data["title"],
                defaults={
                    "author": user,
                    "excerpt": news_data["excerpt"],
                    "content": news_data["content"],
                    "category": news_data["category"],
                    "is_published": news_data["is_published"],
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created news post: {news_post.title}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"News post already exists: {news_post.title}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {created_count} sample news posts"
            )
        )





