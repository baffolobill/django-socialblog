# coding: utf-8
from datetime import datetime
from unidecode import unidecode

from django.db import models
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contirb.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import utc
from django.utils.text import slugify
#from django.db.models import signals

from taggit.managers import TaggableManager
from voter.models import RatingField

try:
    from notification import models as notification
except ImportError:
    notification = None

from socialblog.settings import MARKUP_CHOICES

now = datetime.utcnow().replace(tzinfo=utc)


class Blog(models.Model):
    """
    The blog model is used to associate a collection of posts with another object.
    example: a group model has a blog that members can submit to.
    """

    title = models.CharField(_(u'Title'), max_length=200)
    slug = models.SlugField(_(u'Slug'))
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    created = models.DateTimeField(_('Created'), default=now())

    class Meta:
        # Enforce unique associations per object
        unique_together = (('title', 'content_type', 'object_id'),)
        verbose_name = _(u'Blog')
        verbose_name_plural = _(u'Blogs')

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('socialblog-blog_detail', None, {
            'content_type_id': self.content_type.id,
            'object_id': self.object_id,
            'slug': self.slug,
            })

    @models.permalink
    def get_feed_url(self):
        return ('socialblog-blog_feed', None, {
            'content_type_id': self.content_type.id,
            'object_id': self.object_id,
            'slug': self.slug,
            })


class BlogUserAccess(models.Model):
    blog = models.ForeignKey(Blog, verbose_name=_(u'Blog'), \
        related_name='blog_user_access_list')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, \
        verbose_name=_(u'User'), related_name='blog_user_access_list')
    is_moderator = models.BooleanField(_(u'Is moderator'), default=False)
    can_read = models.BooleanField(_(u'Can read'), default=True)
    can_write = models.BooleanField(_(u'Can write'), default=False)


class PostManager(models.Manager):

    def public(self):
        return self.get_query_set().filter(status=Post.IS_PUBLIC)


class Post(models.Model):
    """Post model."""
    IS_DELETED = 0
    IS_DRAFT = 1
    IS_PUBLIC = 2

    STATUS_CHOICES = (
        (IS_DRAFT, _(u'Draft')),
        (IS_PUBLIC, _(u'Public')),
        (IS_DELETED, _(u'Deleted')),
    )

    blog = models.ForeignKey(Blog, verbose_name=_(u'Blog'), related_name='post_list')
    title = models.CharField(_(u'Title'), max_length=200)
    slug = models.SlugField(_(u'Slug'))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="added_posts")
    creator_ip = models.IPAddressField(_(u"IP Address of the Post Creator"), blank=True, null=True)
    body = models.TextField(_(u'Body'))
    tease = models.TextField(_(u'Tease'), blank=True)
    status = models.IntegerField(_(u'Status'), choices=STATUS_CHOICES, default=IS_DRAFT)
    allow_comments = models.BooleanField(_(u'Allow comments'), default=True)
    comments_count = models.PositiveIntegerField(_(u'Comments Count'), default=0)
    last_comment_datetime = models.DateTimeField(_(u'Date of Last Comment'), default=now())
    markup = models.CharField(_(u"Post Content Markup"), max_length=3, \
                                choices=MARKUP_CHOICES, null=True, blank=True)
    publish = models.DateTimeField(_('Publish'), default=now())

    created = models.DateTimeField(_(u'Created at'), default=now())
    updated = models.DateTimeField(_(u'Updated at'), default=now())

    tags = TaggableManager()
    rating = RatingField(related_name="post_list")
    rating_score = models.FloatField(_(u"Rating score"), default=0)

    objects = PostManager()

    class Meta:
        verbose_name = _(u'Post')
        verbose_name_plural = _(u'Posts')
        ordering = ('-publish',)
        get_latest_by = 'publish'
        unique_together = ('author', 'slug')

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('socialblog-post_detail', None, {
            'content_type_id': self.blog.content_type.id,
            'object_id': self.object_id,
            'blog_slug': self.blog.slug,
            'slug': self.slug,
        })

    def save(self, **kwargs):
        self.updated = now()
        if not self.pk:
            super(Post, self).save(**kwargs)

        if not self.slug:
            self.slug = '%d-%s' % (self.pk, slugify(unidecode(self.title)))
            self.slug = self.slug[:50]

            super(Post, self).save(**kwargs)

    @property
    def is_public(self):
        return self.status == self.IS_PUBLIC

    def is_visible_for_user(self, user):
        return self.is_public or self.author == user

    def can_comment(self, user):
        return self.allow_comments

    def can_edit(self, user):
        return user.is_authenticated() and (self.author == user or \
            (self.blog and self.blog.blog_user_access_list.filter(user=user, is_moderator=True).exists()))

    def get_owners(self):
        return [self.author, ]


# handle notification of new comments
#from threadedcomments.models import ThreadedComment
#def new_comment(sender, instance, **kwargs):
#    if isinstance(instance.content_object, Post):
#        post = instance.content_object
#        if notification:
#            notification.send([post.author], "blog_post_comment", {"user": instance.user, "post": post, "comment": instance})
#signals.post_save.connect(new_comment, sender=ThreadedComment)
