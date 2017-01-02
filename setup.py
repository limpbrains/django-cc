from setuptools import setup, find_packages
from os.path import join, dirname


setup(
    author='Ivan Vershigora',
    author_email='ivan.vershigora@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Build Tools',
    ],
    description='Django wallet for Bitcoin and other cryptocurrencies',
    download_url = 'https://github.com/limpbrains/django-cc/tarball/0.2.1',
    install_requires=[
        'celery>=3,<4',
        'Django>=1.7',
        'mock',
        'pycoin',
        'python-bitcoinrpc>=1.0',
    ],
    keywords='bitcoin litecoin django wallet cryptocurrency',
    license='MIT License',
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    name='django-cc',
    packages=find_packages(),
    url='https://github.com/limpbrains/django-cc',
    version='0.2.1',
)
