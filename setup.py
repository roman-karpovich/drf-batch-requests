import os

from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='drf-batch-requests',
    version='0.0.1',
    packages=['drf_batch', ],
    include_package_data=True,
    license='BSD License',
    description='Facebook-like implementation of batch requests',
    long_description=README,
    keywords='django django-rest-framework drf batch',
    url='https://github.com/roman-karpovich/drf-batch-requests',
    author='Roman Karpovich',
    author_email='fpm.th13f@gmail.com',
    install_requires=[
        'django',
        # 'drf-batch-requests',
    ],
    classifiers=[
        # 'Development Status :: 3 - Alpha',
        # 'Environment :: Web Environment',
        # 'Framework :: Django',
        # 'Intended Audience :: Developers',
        # 'License :: OSI Approved :: BSD License',
        # 'Operating System :: OS Independent',
        # 'Programming Language :: Python',
        # 'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.6',
        # 'Programming Language :: Python :: 2.7',
        # 'Topic :: Internet :: WWW/HTTP',
        # 'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    zip_safe=True
)
