import io
from setuptools import setup, find_packages
from scrapy_accessory import VERSION


with io.open("README.md", "r", encoding="utf8") as f:
    readme = f.read()


setup(
    name='scrapy-accessory',
    version=VERSION,
    license='BSD',
    author='wuwentao',
    author_email='wwtg99@126.com',
    description='A simple accessory tools for Scrapy.',
    long_description=readme,
    long_description_content_type='text/markdown',
    zip_safe=False,
    platforms='any',
    packages=find_packages(),
    python_requires='>=3.4',
    install_requires=['scrapy>=1.7'],
    keywords="scrapy middleware",
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
