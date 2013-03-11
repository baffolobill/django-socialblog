from django.conf import settings


MARKUP_CHOICES_DEFAULT = (
    ('rst', _(u'reStructuredText')),
    ('txl', _(u'Textile')),
    ('mrk', _(u'Markdown')),
)
MARKUP_CHOICES = getattr(settings, 'SOCIALBLOG_MARKUP_CHOICES', MARKUP_CHOICES_DEFAULT)

POST_NAME_MIN_LENGTH = getattr(settings, 'SOCIALBLOG_POST_NAME_MIN_LENGTH', 3)

SHORT_POST_MAX_LENGTH = getattr(settings, 'SOCIALBLOG_SHORT_POST_MAX_LENGTH', 2048)

CUT_MAX_LENGTH = getattr(settings, 'SOCIALBLOG_CUT_MAX_LENGTH', 2048)

CUT_TAG = getattr(settings, 'SOCIALBLOG_CUT_TAG', '<hr class="editor-cut"/>')

CUT_TAG_SYNONYMS = getattr(settings, 'SOCIALBLOG_CUT_TAG_SYNONYMS', ['<!--more-->', '<!--cut-->'])

ITEMS_PER_FEED = getattr(settings, 'SOCIALBLOG_ITEMS_PER_FEED', 20)

DEFAULT_FEED_TITLE = getattr(settings, 'SOCIALBLOG_DEFAULT_FEED_TITLE', 'SportsCorner Users Blogs Posts')

USER_FEED_TITLE = getattr(settings, 'SOCIALBLOG_USER_FEED_TITLE', '%s Blog Posts')

USER_LINK_FN = getattr(settings, 'SOCIALBLOG_USER_LINK_FN', lambda p: p.get_profile().get_absolute_url())
