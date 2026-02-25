"""
Sitemaps for SEO: static pages, churches, events, ministries, news.
When a new church is created (and approved), it is included automatically.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from .models import Church, Event, Ministry, News


class StaticViewSitemap(Sitemap):
    """Static pages that don't change often."""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return [
            ('smart_home', 1.0, 'daily'),   # Root - redirects to nearest church
            ('home', 0.95, 'daily'),        # Global homepage (canonical for "main" site)
            ('events', 0.9, 'daily'),
            ('calendar', 0.85, 'daily'),
            ('ministries', 0.9, 'weekly'),
            ('church_list', 0.95, 'daily'), # All churches directory
            ('about', 0.7, 'monthly'),
            ('leadership', 0.7, 'monthly'),
            ('resources', 0.6, 'monthly'),
            ('testimonies', 0.6, 'monthly'),
            ('volunteer', 0.6, 'monthly'),
            ('prayer_request', 0.7, 'monthly'),
            ('contact', 0.7, 'monthly'),
            ('services', 0.7, 'monthly'),
            ('privacy', 0.4, 'yearly'),
            ('terms', 0.4, 'yearly'),
            ('cookies', 0.4, 'yearly'),
            ('donation', 0.6, 'monthly'),
            ('shop', 0.6, 'weekly'),
            ('watch', 0.7, 'weekly'),
            ('visit', 0.7, 'monthly'),
            ('sermon', 0.7, 'weekly'),
            ('newsletter-signup', 0.5, 'monthly'),
        ]

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]

    def changefreq(self, item):
        return item[2]


class ChurchSitemap(Sitemap):
    """All active, approved churches. New churches appear here automatically when approved."""
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Church.objects.filter(is_active=True, is_approved=True).order_by('name')

    def location(self, church):
        return reverse('church_detail', kwargs={'church_id': church.id})

    def lastmod(self, church):
        return church.updated_at


class ChurchPagesSitemap(Sitemap):
    """Church hub and subpages: church/<id>/, church/<id>/events/, about/, etc."""
    changefreq = 'weekly'
    priority = 0.85

    def items(self):
        churches = Church.objects.filter(is_active=True, is_approved=True)
        entries = []
        for church in churches:
            entries.append((church, 'church_home'))
            entries.append((church, 'church_events'))
            entries.append((church, 'church_ministries'))
            entries.append((church, 'church_sermons'))
            entries.append((church, 'church_news'))
            entries.append((church, 'church_about'))
            entries.append((church, 'church_calendar'))
            entries.append((church, 'church_leadership'))
            entries.append((church, 'church_watch'))
            entries.append((church, 'church_donation'))
        return entries

    def location(self, item):
        church, view_name = item
        if view_name == 'church_donation':
            return reverse('church_donation', kwargs={'church_id': church.id})
        return reverse(view_name, kwargs={'church_id': church.id})

    def lastmod(self, item):
        return item[0].updated_at


class EventSitemap(Sitemap):
    """Global event detail pages (events/<uuid>/)."""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Event.objects.filter(is_public=True).select_related('church').order_by('-start_date')

    def location(self, event):
        return reverse('event_detail', kwargs={'event_id': event.id})

    def lastmod(self, event):
        return event.updated_at


class ChurchEventSitemap(Sitemap):
    """Church-specific event pages (church/<id>/events/<event_id>/)."""
    changefreq = 'weekly'
    priority = 0.75

    def items(self):
        return Event.objects.filter(is_public=True, church__is_active=True, church__is_approved=True).select_related('church').order_by('-start_date')

    def location(self, event):
        return reverse('church_event_detail', kwargs={'church_id': event.church_id, 'event_id': event.id})

    def lastmod(self, event):
        return event.updated_at


class MinistrySitemap(Sitemap):
    """Global ministry detail pages (ministries/<uuid>/)."""
    changefreq = 'monthly'
    priority = 0.75

    def items(self):
        return Ministry.objects.all().select_related('church').filter(church__is_active=True, church__is_approved=True).order_by('name')

    def location(self, ministry):
        return reverse('ministry_detail', kwargs={'ministry_id': ministry.id})

    def lastmod(self, ministry):
        return ministry.updated_at


class ChurchMinistrySitemap(Sitemap):
    """Church-specific ministry pages (church/<id>/ministries/<id>/)."""
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Ministry.objects.filter(church__is_active=True, church__is_approved=True).select_related('church').order_by('name')

    def location(self, ministry):
        return reverse('church_ministry_detail', kwargs={'church_id': ministry.church_id, 'ministry_id': ministry.id})

    def lastmod(self, ministry):
        return ministry.updated_at


class NewsSitemap(Sitemap):
    """News detail pages (news/<uuid>/)."""
    changefreq = 'weekly'
    priority = 0.75

    def items(self):
        return News.objects.filter(is_public=True).select_related('church').filter(church__is_active=True, church__is_approved=True).order_by('-date')

    def location(self, news):
        return reverse('news_detail', kwargs={'news_id': news.id})

    def lastmod(self, news):
        return news.updated_at
