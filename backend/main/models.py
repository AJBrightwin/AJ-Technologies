"""
Database models for the AJ Technologies website.

The tables live in Supabase and are created by supabase_schema.sql, NOT by Django
(managed = False). The separate admin dashboard project reads and writes the same tables.
Full column reference: DATABASE_CONTRACT.md
"""
from django.conf import settings
from django.db import models


class ContactEnquiry(models.Model):
    """One row for every quote request sent from the website (home form, contact form, WhatsApp button)."""

    class Timeline(models.TextChoices):
        ASAP = 'asap', 'As soon as possible'
        ONE_MONTH = '1m', 'Within a month'
        THREE_MONTHS = '3m', '1–3 months'
        EXPLORING = 'explore', 'Just exploring'

    class ContactMethod(models.TextChoices):
        WHATSAPP = 'whatsapp', 'WhatsApp'
        CALL = 'call', 'Phone call'
        EMAIL = 'email', 'Email'

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    email = models.CharField(max_length=254, blank=True, default='')
    business_name = models.CharField(max_length=160, blank=True, default='')
    services = models.JSONField(default=list, blank=True)
    timeline = models.CharField(max_length=10, blank=True, default='')
    contact_method = models.CharField(max_length=10, blank=True, default='')
    message = models.TextField(blank=True, default='')
    source = models.CharField(max_length=10, default='contact')          # home | contact
    submitted_via = models.CharField(max_length=10, default='form')      # form | whatsapp
    language = models.CharField(max_length=2, default='en')              # en | ta
    status = models.CharField(max_length=10, default='new')              # managed in the dashboard
    notes = models.TextField(blank=True, default='')                     # managed in the dashboard
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'contact_enquiries'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} · {self.phone}'


class ShowcaseProject(models.Model):
    """A project shown on the Portfolio page (and up to 3 on the home page). Read-only for the website."""

    id = models.BigAutoField(primary_key=True)
    title_en = models.CharField(max_length=150)
    title_ta = models.CharField(max_length=200, blank=True)
    business_type_en = models.CharField(max_length=150)
    business_type_ta = models.CharField(max_length=200, blank=True)
    built_en = models.TextField()
    built_ta = models.TextField(blank=True)
    tags_en = models.JSONField(default=list)
    tags_ta = models.JSONField(default=list)
    category = models.CharField(max_length=10)          # web | shop | app | mkt
    kind = models.CharField(max_length=10)              # site | app
    image_path = models.CharField(max_length=500, blank=True)
    color_primary = models.CharField(max_length=7)
    color_secondary = models.CharField(max_length=7)
    live_url = models.CharField(max_length=300, blank=True)
    is_sample = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    show_on_home = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'showcase_projects'
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.title_en

    @property
    def image_url(self):
        """Public link to the image in the Supabase Storage bucket.
        image_path is the file's path inside the bucket (e.g. "projects/bakery.jpg");
        a full https:// link is also accepted."""
        path = (self.image_path or '').strip()
        if not path:
            return ''
        if path.startswith(('http://', 'https://')):
            return path
        base = settings.SUPABASE_URL.rstrip('/')
        if not base:
            return ''
        return f'{base}/storage/v1/object/public/{settings.SUPABASE_STORAGE_BUCKET}/{path.lstrip("/")}'

    def to_public_dict(self):
        """Shape used by the website's JavaScript."""
        return {
            'id': self.pk,
            'cat': self.category,
            'kind': self.kind,
            'c1': self.color_primary,
            'c2': self.color_secondary,
            'sample': self.is_sample,
            'link': self.live_url,
            'image': self.image_url,
            'title': {'en': self.title_en, 'ta': self.title_ta or self.title_en},
            'type': {'en': self.business_type_en, 'ta': self.business_type_ta or self.business_type_en},
            'built': {'en': self.built_en, 'ta': self.built_ta or self.built_en},
            'tags': {'en': list(self.tags_en or []), 'ta': list(self.tags_ta or self.tags_en or [])},
        }