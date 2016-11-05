from setuptools import setup, find_packages
from os.path import join, dirname


setup(
    name='django-cc',
    version='0.2',
    license='MIT License',
    description='Django wallet for Bitcoin and other cryptocurrencies',
    author='Ivan Vershigora',
    author_email='ivan.vershigora@gmail.com',
    url='https://github.com/limpbrains/django-cc',
    download_url = 'https://github.com/limpbrains/django-cc/tarball/0.2',
    keywords='bitcoin litecoin django wallet',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    install_requires=[
        'Django>=1.7',
        'celery',
        'pycoin',
        'python-bitcoinrpc>=1.0'
    ]
)
