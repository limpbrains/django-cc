from setuptools import setup, find_packages
from os.path import join, dirname


setup(
    name='django-cc',
    version='0.1.1',
    license='MIT License',
    description='Django wallet for Bitcoin and other cryptocurrencies',
    author='Ivan Vershigora',
    author_email='ivan.vershigora@gmail.com',
    url='https://github.com/limpbrains/django-cc',
    download_url = 'https://github.com/limpbrains/django-cc/tarball/0.1.1',
    keywords='bitcoin litecoin django wallet',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    install_requires=[
        # TODO add python-bitcoinaddress and python-bitcoinrpc when new version will be released
        'Django>=1.7',
        'celery'
    ]
)
