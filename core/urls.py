from django.urls import path
from .views import (
    home, smart_home, events, event_detail, ministries, ministry_detail, newsletter_signup, calendar_view,
    EventListView, MinistryListView, NewsListView, NewsletterSignupCreateView, event_ics,
    about, donation, shop, watch, visit, sermon, church_list, church_detail, church_donation,
    church_home, church_events, church_event_detail, church_ministries, church_ministry_detail,
    church_sermons, church_news, church_about, church_calendar,
    local_admin_dashboard, local_admin_events, local_admin_ministries, local_admin_news,
    local_admin_sermons, local_admin_donations, local_admin_heroes, local_admin_church_settings,
    global_admin_dashboard, request_global_event_feature, global_event_feature_requests,
    request_global_hero_feature, request_global_news_feature, global_hero_feature_requests,
    global_news_feature_requests, privacy, terms, cookies, leadership, resources, testimonies,
    church_leadership, event_highlight_detail, event_speakers,
    all_event_highlights, news_detail,
    check_production_status, debug_env, test_local_upload_endpoint, upload_test_endpoint,
    health_check, startup_health_check, static_fallback, clear_redirect_notification,
)

urlpatterns = [
    path('', smart_home, name='smart_home'),  # New smart home that redirects to nearest church
    path('global/', home, name='home'),  # Global site moved to /global/
    path('events/', events, name='events'),
    path('events/calendar/', calendar_view, name='calendar'),
    path('events/<uuid:event_id>/', event_detail, name='event_detail'),
    path('events/<uuid:event_id>/register/', event_detail, name='event_registration'),
    path('events/<uuid:event_id>/add-to-calendar/', event_ics, name='event_ics'),
    path('ministries/', ministries, name='ministries'),
    path('ministries/<uuid:ministry_id>/', ministry_detail, name='ministry_detail'),
    path('news/<uuid:news_id>/', news_detail, name='news_detail'),
    path('newsletter-signup/', newsletter_signup, name='newsletter-signup'),
    # Church directory
    path('churches/', church_list, name='church_list'),
    path('churches/<uuid:church_id>/', church_detail, name='church_detail'),
    path('churches/<uuid:church_id>/donate/', church_donation, name='church_donation'),
    # Church-specific website (mirrors main site functionality)
    path('church/<uuid:church_id>/', church_home, name='church_home'),
    path('church/<uuid:church_id>/events/', church_events, name='church_events'),
    path('church/<uuid:church_id>/events/<uuid:event_id>/', church_event_detail, name='church_event_detail'),
    path('church/<uuid:church_id>/ministries/', church_ministries, name='church_ministries'),
    path('church/<uuid:church_id>/ministries/<uuid:ministry_id>/', church_ministry_detail, name='church_ministry_detail'),
    path('church/<uuid:church_id>/sermons/', church_sermons, name='church_sermons'),
    path('church/<uuid:church_id>/news/', church_news, name='church_news'),
    path('church/<uuid:church_id>/about/', church_about, name='church_about'),
    path('church/<uuid:church_id>/calendar/', church_calendar, name='church_calendar'),
    path('church/<uuid:church_id>/leadership/', church_leadership, name='church_leadership'),
    # Local Admin Dashboard
    path('local-admin/', local_admin_dashboard, name='local_admin_dashboard'),
    path('local-admin/events/', local_admin_events, name='local_admin_events'),
    path('local-admin/ministries/', local_admin_ministries, name='local_admin_ministries'),
    path('local-admin/news/', local_admin_news, name='local_admin_news'),
    path('local-admin/sermons/', local_admin_sermons, name='local_admin_sermons'),
    path('local-admin/donations/', local_admin_donations, name='local_admin_donations'),
    path('local-admin/heroes/', local_admin_heroes, name='local_admin_heroes'),
    path('local-admin/settings/', local_admin_church_settings, name='local_admin_church_settings'),
    path('local-admin/events/request-global-feature/<uuid:event_id>/', request_global_event_feature, name='request_global_event_feature'),
    path('local-admin/heroes/request-global-feature/<uuid:hero_id>/', request_global_hero_feature, name='request_global_hero_feature'),
    path('local-admin/news/request-global-feature/<uuid:news_id>/', request_global_news_feature, name='request_global_news_feature'),
    # Global Admin Dashboard
    path('global-admin/', global_admin_dashboard, name='global_admin_dashboard'),
    path('global-admin/event-feature-requests/', global_event_feature_requests, name='global_event_feature_requests'),
    path('global-admin/hero-feature-requests/', global_hero_feature_requests, name='global_hero_feature_requests'),
    path('global-admin/news-feature-requests/', global_news_feature_requests, name='global_news_feature_requests'),
    # Placeholder pages
    path('about/', about, name='about'),
    path('leadership/', leadership, name='leadership'),
    path('resources/', resources, name='resources'),
    path('testimonies/', testimonies, name='testimonies'),
    path('privacy/', privacy, name='privacy'),
    path('terms/', terms, name='terms'),
    path('cookies/', cookies, name='cookies'),
    path('donation/', donation, name='donation'),
    path('shop/', shop, name='shop'),
    path('watch/', watch, name='watch'),
    path('visit/', visit, name='visit'),
    path('sermon/', sermon, name='sermon'),
    # API endpoints
    path('api/events/', EventListView.as_view(), name='event-list'),
    path('api/ministries/', MinistryListView.as_view(), name='ministry-list'),
    path('api/news/', NewsListView.as_view(), name='news-list'),
    path('api/newsletter-signup/', NewsletterSignupCreateView.as_view(), name='newsletter-signup-api'),
    path('events/highlight/<uuid:highlight_id>/', event_highlight_detail, name='event_highlight_detail'),
    path('events/<uuid:event_id>/speakers/', event_speakers, name='event_speakers'),
    path('events/highlights/', all_event_highlights, name='all_event_highlights'),
    # Debug views
    path('check-production-status/', check_production_status, name='check_production_status'),
    path('debug-env/', debug_env, name='debug_env'),
    path('test-imagekit-upload/', test_local_upload_endpoint, name='test_imagekit_upload'),
    path('upload-test/', upload_test_endpoint, name='upload_test'),
    path('health/', health_check, name='health_check'),
    path('startup-health/', startup_health_check, name='startup_health_check'),
    path('fallback/', static_fallback, name='static_fallback'),
    path('clear-redirect-notification/', clear_redirect_notification, name='clear_redirect_notification'),
]

urlpatterns += [
    # Removed debug, migration, and fix URLs
] 
