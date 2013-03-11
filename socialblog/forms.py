# coding: utf-8

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags

from socialblog.models import Post
from socialblog.settings import POST_NAME_MIN_LENGTH
from socialblog.settings import CUT_TAG
from socialblog.settings import CUT_TAG_SYNONYMS
from socialblog.settings import SHORT_POST_MAX_LENGTH
from socialblog.settings import CUT_MAX_LENGTH


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('blog', 'slug', 'author', 'creator_ip', \
            'created', 'updated', 'publish', 'comments_count', \
            'last_comment_datetime', 'tags', 'tease', 'status',)

    def __init__(self, request, *args, **kwargs):
        self.user = request.user
        super(PostForm, self).__init__(request.POST or None, *args, **kwargs)

    def clean_title(self):
        title = self.cleaned_data['title'].strip().capitalize()

        if len(title) < POST_NAME_MIN_LENGTH:
            raise forms.ValidationError(_(u"Post title should be at least %s characters.")%POST_NAME_MIN_LENGTH)

        return title

    def clean_body(self):
        body = self.cleaned_data['body']

        for tag in CUT_TAG_SYNONYMS:
            body = body.replace(tag, CUT_TAG)

        editor_cut = body.find(CUT_TAG)
        if editor_cut >= 0:
            tease = strip_tags(body[:editor_cut])
        else:
            tease = ''

        body = strip_tags(body)

        if len(body) > SHORT_POST_MAX_LENGTH and editor_cut < 0:
            raise forms.ValidationError(_(u"Your post is too long and without a cut. Please add cut somewhere to leave only introduction part before it."))

        if editor_cut > CUT_MAX_LENGTH:
            raise forms.ValidationError(_(u"Your cut is too long. Please put the cut somewhere to leave only introduction part no longer, than %s characters before it.") % CUT_MAX_LENGTH)

        self.cleaned_data['tease'] = tease

        return body

    def save(self, *args, **kwargs):
        commit = kwargs.get('commit', True)
        kwargs['commit'] = False

        post = super(PostForm, self).save(*args, **kwargs)
        post.tease = self.cleaned_data['tease']
        post.body = self.cleaned_data['body']

        if commit:
            post.save()

        return post
