# coding: utf-8

from django.conf.urls import patterns, url

from socialblog import views
from socialblog.feeds import (BlogFeedAll, BlogFeedBlog, BlogFeedUser)


urlpatterns = patterns('',
    # all posts across all blogs
    url(r'^$', views.PostList.as_view(), name='socialblog-post_list'),

    # all posts of a blog a.k.a. blog detail
    url(r'^(?P<content_type_id>\d+)/(?P<object_id>\d+)/(?P<slug>[-\w]+)/$',
        views.BlogDetail.as_view(), name='socialblog-blog_detail'),

    # post detail
    url(r'^(?P<content_type_id>\d+)/(?P<object_id>\d+)/(?P<blog_slug>[-\w]+)/(?P<slug>[-\w]+)/$',
        views.PostDetail.as_view(), name='socialblog-post_detail'),

    # add/edit/delete post
    url(r'^add/$', views.post_add, name='socialblog-post_add'),
    url(r'^edit/(?P<object_id>\d+)/$', views.post_edit, name='socialblog-post_edit'),
    url(r'^delete/(?P<object_id>\d+)/$', views.post_delete, name='socialblog-post_delete'),
    url(r'^(?P<action>draft|public)/(?P<object_id>\d+)/$', views.post_change_status,
        name='socialblog-post_change_status'),


    # feeds
    url(r'^feed/posts/all/$', BlogFeedAll(), name='socialblog-post_list_feed'),
    url(r'^feed/(?P<content_type_id>\d+)/(?P<object_id>\d+)/(?P<slug>[-\w]+)/$',
        BlogFeedBlog, name='socialblog-blog_feed'),
    url(r'^feed/posts/only/(?P<username>[\w\._\-]+)/$', BlogFeedUser(),
        name='socialblog-user_post_list_feed'),
)
