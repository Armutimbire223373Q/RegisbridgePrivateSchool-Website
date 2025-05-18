from django.core.management.base import BaseCommand
from core.models import HomePageContent, NewsItem, Event
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Creates homepage content for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating homepage content...')

        # Delete existing homepage content
        HomePageContent.objects.all().delete()

        # Create homepage content
        homepage = HomePageContent.objects.create(
            title="Welcome to Regisbridge Private School",
            subtitle="Empowering minds, shaping futures",
            hero_text="Welcome to Regisbridge Private School, where excellence meets innovation in education.",
            about_section="""
            Regisbridge Private School is a leading educational institution committed to providing exceptional education 
            and fostering academic excellence. With state-of-the-art facilities and dedicated faculty, we prepare 
            students for success in an ever-evolving global landscape.
            """,
            mission_statement="""
            Our mission is to provide a nurturing environment that promotes academic excellence, personal growth, 
            and character development. We strive to empower students with knowledge, skills, and values necessary 
            for lifelong success.
            """,
            vision_statement="""
            To be a globally recognized institution of academic excellence, producing leaders who contribute 
            positively to society through innovation, integrity, and compassion.
            """,
            contact_email="info@regisbridge.edu",
            contact_phone="+1 234 567 8900",
            address="123 Education Avenue, Knowledge City, ST 12345",
            facebook_url="https://facebook.com/regisbridge",
            twitter_url="https://twitter.com/regisbridge",
            instagram_url="https://instagram.com/regisbridge",
            youtube_url="https://youtube.com/regisbridge"
        )

        # Create news items
        news_items = [
            {
                'title': 'Academic Excellence Awards 2024',
                'content': 'Join us in celebrating our students outstanding achievements at the annual Academic Excellence Awards ceremony.',
                'date_posted': timezone.now() - timedelta(days=2),
                'image': 'news/academic_awards.jpg',
                'is_published': True
            },
            {
                'title': 'New STEM Lab Opening',
                'content': 'We are excited to announce the opening of our state-of-the-art STEM laboratory.',
                'date_posted': timezone.now() - timedelta(days=5),
                'image': 'news/stem_lab.jpg',
                'is_published': True
            },
            {
                'title': 'Sports Championship Victory',
                'content': 'Our school team wins the regional sports championship for the third consecutive year.',
                'date_posted': timezone.now() - timedelta(days=7),
                'image': 'news/sports_victory.jpg',
                'is_published': True
            }
        ]

        for item in news_items:
            NewsItem.objects.create(**item)

        # Create events
        events = [
            {
                'title': 'Annual Science Fair',
                'description': 'Students showcase their innovative science projects.',
                'start_date': timezone.now() + timedelta(days=15),
                'end_date': timezone.now() + timedelta(days=15, hours=8),
                'location': 'School Auditorium',
                'image': 'events/science_fair.jpg',
                'is_featured': True
            },
            {
                'title': 'Parent-Teacher Conference',
                'description': 'Discuss student progress and academic performance.',
                'start_date': timezone.now() + timedelta(days=7),
                'end_date': timezone.now() + timedelta(days=7, hours=6),
                'location': 'School Conference Hall',
                'image': 'events/ptc.jpg',
                'is_featured': True
            },
            {
                'title': 'Cultural Festival',
                'description': 'Celebrate diversity through music, dance, and art.',
                'start_date': timezone.now() + timedelta(days=30),
                'end_date': timezone.now() + timedelta(days=30, hours=12),
                'location': 'School Grounds',
                'image': 'events/cultural_fest.jpg',
                'is_featured': True
            }
        ]

        for event in events:
            Event.objects.create(**event)

        self.stdout.write(self.style.SUCCESS('Successfully created homepage content')) 