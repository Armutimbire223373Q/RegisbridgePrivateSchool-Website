from django.db import migrations

def create_initial_content(apps, schema_editor):
    HomePageContent = apps.get_model('core', 'HomePageContent')
    NewsItem = apps.get_model('core', 'NewsItem')
    Event = apps.get_model('core', 'Event')

    # Create homepage content
    HomePageContent.objects.create(
        title='Welcome to Regisbridge Private School',
        subtitle='Empowering minds, shaping futures',
        hero_text='Welcome to Regisbridge Private School, where excellence meets innovation in education.',
        about_section='Regisbridge Private School is a leading educational institution committed to providing exceptional education.',
        mission_statement='Our mission is to provide exceptional education that empowers students to achieve their full potential.',
        vision_statement='Our vision is to be a leading educational institution that nurtures future leaders and innovators.',
        contact_email='contact@regisbridge.com',
        contact_phone='+1234567890',
        address='123 School Street, City, State, ZIP'
    )

    # Create sample news items
    news_items = [
        {
            'title': 'New Academic Year Begins',
            'content': 'We are excited to welcome our students back for another year of learning and growth.',
            'is_published': True
        },
        {
            'title': 'Science Fair Winners Announced',
            'content': 'Congratulations to all participants in this year\'s Science Fair.',
            'is_published': True
        },
        {
            'title': 'Sports Day Coming Up',
            'content': 'Join us for our annual Sports Day celebration next month.',
            'is_published': True
        }
    ]
    
    for news_item in news_items:
        NewsItem.objects.create(**news_item)

    # Create sample events
    events = [
        {
            'title': 'Parent-Teacher Conference',
            'description': 'Meet with teachers to discuss your child\'s progress.',
            'start_date': '2025-06-01T09:00:00Z',
            'end_date': '2025-06-01T17:00:00Z',
            'location': 'School Auditorium',
            'is_featured': True
        },
        {
            'title': 'Annual Science Fair',
            'description': 'Students showcase their innovative science projects.',
            'start_date': '2025-06-15T10:00:00Z',
            'end_date': '2025-06-15T16:00:00Z',
            'location': 'School Gymnasium',
            'is_featured': True
        },
        {
            'title': 'Sports Day',
            'description': 'A day of athletic competitions and team spirit.',
            'start_date': '2025-06-30T08:00:00Z',
            'end_date': '2025-06-30T16:00:00Z',
            'location': 'School Sports Ground',
            'is_featured': True
        }
    ]
    
    for event in events:
        Event.objects.create(**event)

def remove_initial_content(apps, schema_editor):
    HomePageContent = apps.get_model('core', 'HomePageContent')
    NewsItem = apps.get_model('core', 'NewsItem')
    Event = apps.get_model('core', 'Event')
    
    HomePageContent.objects.all().delete()
    NewsItem.objects.all().delete()
    Event.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_content, remove_initial_content),
    ] 