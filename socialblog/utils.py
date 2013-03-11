# coding: utf-8

import urlparse

from django.http import Http404
from django.shortcuts import redirect


def safe_redirect(url_or_name, request):
    netloc = urlparse.urlparse(url_or_name)[1]

    if netloc and netloc != request.get_host():
        raise Http404

    return redirect(url_or_name)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
