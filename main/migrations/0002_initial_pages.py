from django.db import migrations

def create_initial_pages(apps, schema_editor):
    Page = apps.get_model('main', 'Page')
    AboutPage = apps.get_model('main', 'AboutPage')
    AcademicsPage = apps.get_model('main', 'AcademicsPage')
    CurriculumPage = apps.get_model('main', 'CurriculumPage')
    StudentLifePage = apps.get_model('main', 'StudentLifePage')
    ContactPage = apps.get_model('main', 'ContactPage')

    # Create About Page
    about_page = Page.objects.create(
        title="About Us",
        slug="about",
        content="Welcome to Regisbridge Private School",
        meta_description="Learn about our history, mission, and values",
        is_published=True
    )
    AboutPage.objects.create(
        page=about_page,
        mission_statement="To provide excellence in education",
        vision_statement="To be a leading institution in holistic education",
        values="Integrity, Excellence, Innovation",
        history="Founded in 2020 with a vision for excellence",
        leadership_team="Our dedicated team of educators"
    )

    # Create Academics Page
    academics_page = Page.objects.create(
        title="Academics",
        slug="academics",
        content="Our academic programs",
        meta_description="Explore our academic offerings",
        is_published=True
    )
    AcademicsPage.objects.create(
        page=academics_page,
        programs_overview="Comprehensive education from K-12",
        curriculum_overview="Our curriculum is designed to challenge and inspire",
        faculty_highlight="Experienced and dedicated faculty",
        academic_support="Comprehensive support services"
    )

    # Create Curriculum Pages for different grade levels
    grade_levels = [
        ('Elementary School', 'elementary'),
        ('Middle School', 'middle'),
        ('High School', 'high')
    ]
    for grade_name, grade_level in grade_levels:
        page = Page.objects.create(
            title=f"{grade_name} Curriculum",
            slug=f"{grade_level}-curriculum",
            content=f"Curriculum details for {grade_name}",
            meta_description=f"Learn about our {grade_name} curriculum",
            is_published=True
        )
        CurriculumPage.objects.create(
            page=page,
            grade_level=grade_level,
            subjects=f"Core subjects for {grade_name}",
            learning_outcomes=f"Key learning objectives for {grade_name}"
        )

    # Create Student Life Page
    student_life_page = Page.objects.create(
        title="Student Life",
        slug="student-life",
        content="Experience life at Regisbridge",
        meta_description="Discover student life and activities",
        is_published=True
    )
    StudentLifePage.objects.create(
        page=student_life_page,
        activities="Various extracurricular activities",
        clubs="Student clubs and organizations",
        sports="Competitive sports programs"
    )

    # Create Contact Page
    contact_page = Page.objects.create(
        title="Contact Us",
        slug="contact",
        content="Get in touch with us",
        meta_description="Contact Regisbridge Private School",
        is_published=True
    )
    ContactPage.objects.create(
        page=contact_page,
        address="123 Education Street, City, State, ZIP",
        phone="+1234567890",
        email="info@regisbridge.edu",
        office_hours="Monday-Friday: 8:00 AM - 4:00 PM"
    )

def remove_initial_pages(apps, schema_editor):
    Page = apps.get_model('main', 'Page')
    Page.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_pages, remove_initial_pages),
    ] 