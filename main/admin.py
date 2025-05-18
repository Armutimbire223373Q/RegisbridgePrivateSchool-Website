from django.contrib import admin
from django.utils.html import format_html
from .models import Page, AboutPage, AcademicsPage, CurriculumPage, StudentLifePage, ContactPage, FAQ

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at', 'updated_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content', 'meta_description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')

class AboutPageInline(admin.StackedInline):
    model = AboutPage
    extra = 1
    max_num = 1

class AcademicsPageInline(admin.StackedInline):
    model = AcademicsPage
    extra = 1
    max_num = 1

class CurriculumPageInline(admin.StackedInline):
    model = CurriculumPage
    extra = 1
    max_num = 1

class StudentLifePageInline(admin.StackedInline):
    model = StudentLifePage
    extra = 1
    max_num = 1

class ContactPageInline(admin.StackedInline):
    model = ContactPage
    extra = 1
    max_num = 1

@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'get_is_published', 'get_created_at')
    list_filter = ('page__is_published', 'page__created_at')
    search_fields = ('page__title', 'page__content', 'mission_statement', 'vision_statement')

    def get_title(self, obj):
        return obj.page.title
    get_title.short_description = 'Title'

    def get_is_published(self, obj):
        return obj.page.is_published
    get_is_published.short_description = 'Published'
    get_is_published.boolean = True

    def get_created_at(self, obj):
        return obj.page.created_at
    get_created_at.short_description = 'Created At'

@admin.register(AcademicsPage)
class AcademicsPageAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'get_is_published', 'get_created_at')
    list_filter = ('page__is_published', 'page__created_at')
    search_fields = ('page__title', 'page__content', 'programs_overview', 'curriculum_overview')

    def get_title(self, obj):
        return obj.page.title
    get_title.short_description = 'Title'

    def get_is_published(self, obj):
        return obj.page.is_published
    get_is_published.short_description = 'Published'
    get_is_published.boolean = True

    def get_created_at(self, obj):
        return obj.page.created_at
    get_created_at.short_description = 'Created At'

@admin.register(CurriculumPage)
class CurriculumPageAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'grade_level', 'get_is_published', 'get_created_at')
    list_filter = ('grade_level', 'page__is_published', 'page__created_at')
    search_fields = ('page__title', 'page__content', 'subjects', 'learning_outcomes')

    def get_title(self, obj):
        return obj.page.title
    get_title.short_description = 'Title'

    def get_is_published(self, obj):
        return obj.page.is_published
    get_is_published.short_description = 'Published'
    get_is_published.boolean = True

    def get_created_at(self, obj):
        return obj.page.created_at
    get_created_at.short_description = 'Created At'

@admin.register(StudentLifePage)
class StudentLifePageAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'get_is_published', 'get_created_at')
    list_filter = ('page__is_published', 'page__created_at')
    search_fields = ('page__title', 'page__content', 'activities', 'clubs', 'sports')

    def get_title(self, obj):
        return obj.page.title
    get_title.short_description = 'Title'

    def get_is_published(self, obj):
        return obj.page.is_published
    get_is_published.short_description = 'Published'
    get_is_published.boolean = True

    def get_created_at(self, obj):
        return obj.page.created_at
    get_created_at.short_description = 'Created At'

@admin.register(ContactPage)
class ContactPageAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'get_is_published', 'get_created_at')
    list_filter = ('page__is_published', 'page__created_at')
    search_fields = ('page__title', 'page__content', 'address', 'email')

    def get_title(self, obj):
        return obj.page.title
    get_title.short_description = 'Title'

    def get_is_published(self, obj):
        return obj.page.is_published
    get_is_published.short_description = 'Published'
    get_is_published.boolean = True

    def get_created_at(self, obj):
        return obj.page.created_at
    get_created_at.short_description = 'Created At'

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_published', 'order', 'created_at')
    list_filter = ('category', 'is_published', 'created_at')
    search_fields = ('question', 'answer')
    ordering = ('order', 'created_at')
