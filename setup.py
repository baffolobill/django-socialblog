import os
from setuptools import setup, find_packages

PACKAGE_NAME = 'socialblog'
PACKAGE_DATA = list()

for directory in [ 'templates', 'static' ]:
    for root, dirs, files in os.walk( os.path.join( PACKAGE_NAME, directory )):
        for filename in files:
            PACKAGE_DATA.append("%s/%s" % ( root[len(PACKAGE_NAME)+1:], filename ))

setup(
    name = "django-socialblog",
    version = "0.0.1",
    description = "A reusable multi-user blogging platform for django social applications",
    author = "Greg Newman",
    author_email = "gregoryjnewman@gmail.com",
    url = "http://code.google.com/p/django-socialblog/",
    packages = find_packages(),
    classifiers = [
        "Development Status :: Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
    include_package_data = True,
    package_data = { '': PACKAGE_DATA, },
    #dependency_links = [
    #    'https://github.com/ProstoKSI/django-voter/archive/master.zip#egg=django-voter',
    #    'https://github.com/ProstoKSI/html-cleaner/archive/master.zip#egg=html-cleaner',
    #],
    install_requires = ['django-atompub', 'Django-Tagging', 'Django-ThreadedComments'],
    zip_safe = False,
)
