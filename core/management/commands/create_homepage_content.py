from django.core.management.base import BaseCommand
from core.models import HomePageContent, NewsItem, Event
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Creates homepage content for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating homepage content...')

        # Create homepage content
        homepage = HomePageContent.objects.get_or_create(
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
            linkedin_url="https://linkedin.com/company/regisbridge"
        )[0]

        # Create news items
        news_items = [
            {
                'title': 'Academic Excellence Awards 2024',
                'content': 'Join us in celebrating our students outstanding achievements at the annual Academic Excellence Awards ceremony.',
                'date': timezone.now() - timedelta(days=2),
                'image_url': 'news/academic_awards.jpg'
            },
            {
                'title': 'New STEM Lab Opening',
                'content': 'We are excited to announce the opening of our state-of-the-art STEM laboratory.',
                'date': timezone.now() - timedelta(days=5),
                'image_url': 'news/stem_lab.jpg'
            },
            {
                'title': 'Sports Championship Victory',
                'content': 'Our school team wins the regional sports championship for the third consecutive year.',
                'date': timezone.now() - timedelta(days=7),
                'image_url': 'news/sports_victory.jpg'
            }
        ]

        for item in news_items:
            NewsItem.objects.get_or_create(
                title=item['title'],
                content=item['content'],
                date=item['date'],
                image_url=item['image_url']
            )

        # Create events
        events = [
            {
                'title': 'Annual Science Fair',
                'description': 'Students showcase their innovative science projects.',
                'date': timezone.now() + timedelta(days=15),
                'time': '09:00:00',
                'location': 'School Auditorium',
                'image_url': 'events/science_fair.jpg'
            },
            {
                'title': 'Parent-Teacher Conference',
                'description': 'Discuss student progress and academic performance.',
                'date': timezone.now() + timedelta(days=7),
                'time': '14:00:00',
                'location': 'School Conference Hall',
                'image_url': 'events/ptc.jpg'
            },
            {
                'title': 'Cultural Festival',
                'description': 'Celebrate diversity through music, dance, and art.',
                'date': timezone.now() + timedelta(days=30),
                'time': '10:00:00',
                'location': 'School Grounds',
                'image_url': 'events/cultural_fest.jpg'
            }
        ]

        for event in events:
            Event.objects.get_or_create(
                title=event['title'],
                description=event['description'],
                date=event['date'],
                time=event['time'],
                location=event['location'],
                image_url=event['image_url']
            )

        self.stdout.write(self.style.SUCCESS('Successfully created homepage content')) 