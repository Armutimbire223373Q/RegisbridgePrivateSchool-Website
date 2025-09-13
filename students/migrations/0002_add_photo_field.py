from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("students", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentprofile",
            name="photo",
            field=models.ImageField(upload_to="student_photos/", blank=True, null=True),
        ),
    ]




