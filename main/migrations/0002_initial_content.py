from django.db import migrations

def create_initial_content(apps, schema_editor):
    Page = apps.get_model('main', 'Page')
    AboutPage = apps.get_model('main', 'AboutPage')
    AcademicsPage = apps.get_model('main', 'AcademicsPage')
    ContactPage = apps.get_model('main', 'ContactPage')
    CurriculumPage = apps.get_model('main', 'CurriculumPage')
    StudentLifePage = apps.get_model('main', 'StudentLifePage')
    FAQ = apps.get_model('main', 'FAQ')

    # Create About Page
    about_page = Page.objects.create(
        title='About Us',
        slug='about',
        content='Welcome to Regisbridge Private School',
        meta_description='Learn about our history, mission, and values.',
        is_published=True
    )
    AboutPage.objects.create(
        page=about_page,
        mission_statement='Our mission is to provide exceptional education that empowers students to achieve their full potential.',
        vision_statement='Our vision is to be a leading educational institution that nurtures future leaders and innovators.',
        values='Excellence, Integrity, Innovation, Respect, and Community',
        history='Founded with a vision of excellence in education, Regisbridge Private School has been serving our community since its establishment.',
        leadership_team='Our leadership team consists of experienced educators and administrators committed to student success.'
    )

    # Create Academics Page
    academics_page = Page.objects.create(
        title='Academics',
        slug='academics',
        content='Our Academic Programs',
        meta_description='Explore our comprehensive academic programs and curriculum.',
        is_published=True
    )
    AcademicsPage.objects.create(
        page=academics_page,
        programs_overview='We offer a comprehensive range of academic programs designed to challenge and inspire students.',
        curriculum_overview='Our curriculum is designed to meet and exceed international standards while fostering creativity and critical thinking.',
        faculty_highlight='Our faculty members are highly qualified professionals with extensive experience in education.',
        academic_support='We provide comprehensive academic support services to ensure every student succeeds.'
    )

    # Create Contact Page
    contact_page = Page.objects.create(
        title='Contact Us',
        slug='contact',
        content='Get in Touch',
        meta_description='Contact Regisbridge Private School. We\'re here to help.',
        is_published=True
    )
    ContactPage.objects.create(
        page=contact_page,
        address='123 School Street, City, State, ZIP',
        phone='+1234567890',
        email='contact@regisbridge.com',
        office_hours='Monday to Friday: 8:00 AM - 4:00 PM',
        map_embed_code='<iframe src="https://www.google.com/maps/embed?..." width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy"></iframe>'
    )

    # Create Curriculum Pages
    for grade_level, title in [
        ('elementary', 'Elementary School Curriculum'),
        ('middle', 'Middle School Curriculum'),
        ('high', 'High School Curriculum')
    ]:
        curriculum_page = Page.objects.create(
            title=title,
            slug=f'curriculum-{grade_level}',
            content=f'{title} Overview',
            meta_description=f'Learn about our {title.lower()}.',
            is_published=True
        )
        CurriculumPage.objects.create(
            page=curriculum_page,
            grade_level=grade_level,
            subjects=f'Our {title.lower()} includes core subjects and enrichment programs.',
            learning_outcomes=f'Students in our {title.lower()} develop essential skills for academic success.'
        )

    # Create Student Life Page
    student_life_page = Page.objects.create(
        title='Student Life',
        slug='student-life',
        content='Experience Life at Regisbridge',
        meta_description='Discover the vibrant student life at Regisbridge Private School.',
        is_published=True
    )
    StudentLifePage.objects.create(
        page=student_life_page,
        activities='We offer a wide range of extracurricular activities that enrich student life.',
        clubs='Join our diverse student clubs and organizations.',
        sports='Our comprehensive sports program promotes teamwork and excellence.'
    )

    # Create FAQs
    faqs_data = [
        {
            'question': 'What are the school hours?',
            'answer': 'School hours are from 8:00 AM to 3:00 PM, Monday through Friday.',
            'category': 'general'
        },
        {
            'question': 'How do I apply for admission?',
            'answer': 'Visit our Admissions page to learn about the application process and requirements.',
            'category': 'admissions'
        },
        {
            'question': 'What is your curriculum based on?',
            'answer': 'Our curriculum follows international standards while incorporating local requirements.',
            'category': 'academics'
        }
    ]
    for i, faq_data in enumerate(faqs_data):
        FAQ.objects.create(
            question=faq_data['question'],
            answer=faq_data['answer'],
            category=faq_data['category'],
            order=i,
            is_published=True
        )

def remove_initial_content(apps, schema_editor):
    Page = apps.get_model('main', 'Page')
    Page.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_content, remove_initial_content),
    ] 