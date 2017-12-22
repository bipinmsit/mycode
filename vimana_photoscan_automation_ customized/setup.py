# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='vimana.photoscan_automation',
    version='0.1.0',
    description='Vimana Photoscan Automation Module',
    long_description=readme,
    author='Abhishek Mishra',
    author_email='abhishek.mishra@aspecscire.com',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
