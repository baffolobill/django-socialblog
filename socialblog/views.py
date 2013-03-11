# coding: utf-8
from django.conf import settings
from django.contib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now as utcnow
from django.views.generic import DetailView, ListView

from voter.models import create_rating

from socialblog.models import Post, Blog
from socialblog.forms import PostForm
from socialblog.signals import post_published
from socialblog.utils import safe_redirect, get_client_ip


## Class-based Views
class BlogDetail(DetailView):

    model = Blog
    template_name = 'socialblog/blog_detail.html'

    def get_object(self):
        ct_id = self.kwargs.get('content_type_id', None)
        object_id = self.kwargs.get('object_id', None)
        blog_slug = self.kwargs.get('slug', None)

        if not (ct_id and object_id and blog_slug):
            return self.model.objects.none()

        return self.model.objects.get(content_type__id=ct_id, \
                                        object_id=object_id, \
                                        slug=blog_slug)

    def get_context_data(self, **kwargs):
        context = super(BlogDetail, self).get_context_data(**kwargs)

        obj = self.get_object()
        if obj:
            context['post_list'] = obj.post_list.filter(status=Post.IS_PUBLIC)

        return context


class PostDetail(DetailView):

    model = Post
    template_name = 'socialblog/blog_post_detail.html'

    def get_object(self):
        """
        TODO:
        1) check if post IS_PUBLIC;
        """
        ct_id = self.kwargs.get('content_type_id', None)
        object_id = self.kwargs.get('object_id', None)
        blog_slug = self.kwargs.get('blog_slug', None)
        slug = self.kwargs.get('slug', None)

        if not (ct_id and object_id and blog_slug and slug):
            return self.model.objects.none()

        return self.model.objects.get(blog__content_type__id=ct_id, \
                                        blog__object_id=object_id, \
                                        blog__slug=blog_slug, \
                                        slug=slug, \
                                        status=Post.IS_PUBLIC)


class PostList(ListView):

    queryset = Post.objects.filter(status=Post.IS_PUBLIC)
    template_name = 'socialblog/post_list.html'


@login_required
def post_change_status(request, action, object_id):
    post = get_object_or_404(Post, pk=object_id)
    if not post.can_edit(request.user):
        messages.error(request, _(u"You can't change status of post that isn't your"))
    else:
        if action == 'draft' and post.status == Post.IS_PUBLIC:
            post.status = Post.IS_DRAFT
        if action == 'public' and post.status == Post.IS_DRAFT:
            post.status = Post.IS_PUBLIC
            post_published.send(sender=Post, post=post)
        post.save()
        messages.success(request, _(u"Successfully change status for post '%s'") % post.title)

    next = request.GET.get('next', post.blog.get_absolute_url())

    return safe_redirect(next, request)


@login_required
def post_add(request, form_class=PostForm, template_name="socialblog/post_add.html"):
    post_form = form_class(request)
    if request.method == "POST" and post_form.is_valid():
        post = post_form.save(commit=False)
        post.author = request.user
        post.rating = create_rating()
        post.creator_ip = get_client_ip(request)
        post.save()
        messages.success(request, _(u"Successfully created post '%s'") % post.title)

        return redirect(post.get_absolute_url())

    return TemplateResponse(request, template_name, \
        {'post_form': post_form, 'current_user': request.user})


@login_required
def post_edit(request, object_id, form_class=PostForm, template_name="socialblog/post_edit.html"):
    post = get_object_or_404(Post, pk=object_id)
    if not post.can_edit(request.user):
        messages.error(request, _(u"You can't edit posts that aren't yours"))
        return redirect(post.blog.get_absolute_url())

    post_form = form_class(request, instance=post)
    if request.method == "POST" and post_form.is_valid():
        post = post_form.save(commit=False)
        post.updated = utcnow()
        post.save()

        messages.success(request, _(u"Successfully updated post '%s'") % post.title)

        return redirect(post.get_absolute_url())

    return TemplateResponse(request, template_name, {"post_form": post_form, "post": post})


@login_required
def post_delete(request, object_id):
    post = get_object_or_404(Post, pk=object_id)
    redirect_to = post.blog.get_absolute_url()
    if not post.can_edit(request.user):
        messages.error(request, _(u"You can't delete posts that aren't yours"))
    else:
        post.delete()

    return redirect(redirect_to)
