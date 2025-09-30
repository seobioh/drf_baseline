# servicies/models.py
app_name = "services"

from django.db import models

class Service:
    SERVICE_CHOICES = [
        ('SERVICE1', 'Service1'),
        ('SERVICE2', 'Service2'),
        ('SERVICE3', 'Service3'),
    ]


class Notice(models.Model):
    service = models.CharField(max_length=20, choices=Service.SERVICE_CHOICES)
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=200, blank=True, null=True)

    mobile_img = models.URLField(max_length=500, blank=True, null=True)
    desktop_img = models.URLField(max_length=500, blank=True, null=True)
    detail_img = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(max_length=500, blank=True, null=True)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Notice'
        verbose_name_plural = 'Notices'

    def __str__(self):
        return f'({self.service} - {self.title})'


class Event(models.Model):
    service = models.CharField(max_length=20, choices=Service.SERVICE_CHOICES)
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=200, blank=True, null=True)

    mobile_img = models.URLField(max_length=500, blank=True, null=True)
    desktop_img = models.URLField(max_length=500, blank=True, null=True)
    detail_img = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(max_length=500, blank=True, null=True)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return f'({self.service} - {self.title})'


class Ad(models.Model):
    service = models.CharField(max_length=20, choices=Service.SERVICE_CHOICES)
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=200, blank=True, null=True)

    mobile_img = models.URLField(max_length=500, blank=True, null=True)
    desktop_img = models.URLField(max_length=500, blank=True, null=True)
    detail_img = models.URLField(max_length=500, blank=True, null=True)
    background_img = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(max_length=500, blank=True, null=True)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Ad'
        verbose_name_plural = 'Ads'

    def __str__(self):
        return f'({self.service} - {self.title})'


class FAQ(models.Model):
    service = models.CharField(max_length=20, choices=Service.SERVICE_CHOICES)
    order = models.PositiveIntegerField(default=1)

    question = models.CharField(max_length=200)
    answer = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return f'({self.service} - {self.question})'


class PrivacyPolicy(models.Model):
    service = models.CharField(max_length=20, choices=Service.SERVICE_CHOICES)
    order = models.PositiveIntegerField(default=1)

    subject = models.CharField(max_length=200)
    detail = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Privacy Policy'
        verbose_name_plural = 'Privacy Policies'

    def __str__(self):
        return f'({self.service} - {self.subject})'


class Term(models.Model):
    service = models.CharField(max_length=20, choices=Service.SERVICE_CHOICES)
    order = models.PositiveIntegerField(default=1)

    subject = models.CharField(max_length=200)
    detail = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Term'
        verbose_name_plural = 'Terms'

    def __str__(self):
        return f'({self.service} - {self.subject})'


class GPTPrompt(models.Model):
    service = models.CharField(max_length=20, choices=Service.SERVICE_CHOICES)

    prompt = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'GPTPrompt'
        verbose_name_plural = 'GPTPrompts'

    def __str__(self):
        return f'({self.service} - {self.prompt})'