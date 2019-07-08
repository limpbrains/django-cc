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
    long_description_content_type="text/markdown",
    download_url = 'https://github.com/limpbrains/django-cc/tarball/0.2.3',
    install_requires=[
        'celery>=3',
        'Django>=1.7',
        'mock',
        'pycoin>=0.90',
        'python-bitcoinrpc>=1.0',
    ],
    keywords='bitcoin django wallet cryptocurrency litecoin zcash dogecoin dash',
    license='MIT License',
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    name='django-cc',
    packages=find_packages(),
    url='https://github.com/limpbrains/django-cc',
    version='0.2.3',
)
