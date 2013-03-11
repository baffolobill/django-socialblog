# coding: utf-8

from django.contrib.auth import get_user_model
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import linebreaks, escape
from django.utils import feedgenerator

from socialblog.models import Post, Blog
from socialblog.settings import ITEMS_PER_FEED
from socialblog.settings import DEFAULT_FEED_TITLE
from socialblog.settings import USER_FEED_TITLE
from socialblog.settings import USER_LINK_FN


class BasePostFeed(Feed):

    feed_type = feedgenerator.Atom1Feed

    def item_title(self, item):
        return item.title

    def item_pubdate(self, item):
        return item.updated

    def item_author_name(self, item):
        return item.author.get_full_name() or item.author.get_username()

    def item_author_link(self, item):
        return USER_LINK_FN(item.author)

    def item_description(self, item):
        if item.tease:
            return linebreaks(escape(item.tease))

        return linebreaks(escape(item.body))


class BlogFeedAll(BasePostFeed):

    title = DEFAULT_FEED_TITLE
    link = reverse('socialblog-post_list_feed')

    def items(self):
        return Post.objects.public().order_by("-updated")[:ITEMS_PER_FEED]


class BlogFeedBlog(BasePostFeed):

    def get_object(self, request, *args, **kwargs):
        ct_id = kwargs.get('content_type_id', None)
        object_id = kwargs.get('object_id', None)
        blog_slug = kwargs.get('slug', None)

        return get_object_or_404(Blog, content_type__id=ct_id, \
                                        object_id=object_id, \
                                        slug=blog_slug)

    def link(self, blog):
        return blog.get_feed_url()

    def title(self, blog):
        return blog.title

    def items(self, blog):
        return Post.objects.public().filter(blog=blog)\
                    .order_by("-updated")[:ITEMS_PER_FEED]


class BlogFeedUser(BasePostFeed):

    def get_object(self, request, *args, **kwargs):
        user_model = get_user_model()
        query = {user_model.USERNAME_FIELD: kwargs.get('username', None)}

        return get_object_or_404(user_model, **query)

    def link(self, user):
        return reverse('socialblog-user_post_list_feed', None, {
            'username': user.get_username(),
            })

    def title(self, user):
        username = user.get_full_name() or user.get_username()
        return USER_FEED_TITLE % username

    def items(self, user):
        return Post.objects.public().filter(author=user)\
                        .order_by("-updated")[:ITEMS_PER_FEED]
