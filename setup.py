import os

from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'readme.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='drf-batch-requests',
    version='0.8.10',
    packages=['drf_batch_requests', ],
    include_package_data=True,
    license='MIT License',
    description='Facebook-like implementation of batch requests',
    long_description=README,
    keywords='django django-rest-framework drf batch',
    url='https://github.com/roman-karpovich/drf-batch-requests',
    author='Roman Karpovich',
    author_email='fpm.th13f@gmail.com',
    install_requires=[
        'django>=1.9',
        'djangorestframework',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    zip_safe=True
)
