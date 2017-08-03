# -*- coding:utf-8 -*-
"""
from setuptools import setup, find_packages

setup(
    name = "bidsSpider",
    version="1.0.0",
    description='a dynamic spider for bids',
    author='jennei',
    packages=find_packages(),
    package_data={'':['*.conf', '*.cfg']},
    include_package_data=True,
    entry_points={
        'console_scripts':['bids=HospitalGenerator.run:main']
    }
)
"""
from distutils.core import setup
import py2exe
import sys
sys.path.append('C:\CocosEnv\Python27\Lib\site-packages\setuptoolsmegg')

includes = ['zope.interface', 'lxml.etree',
            'lxml._elementpath', 'gzip',
            'scrapy.spiderloader','xmlrpclib',
            'scrapy', 'os', 'twisted',
            'sqlalchemy.sql.default_comparator',
            'scrapy.statscollectors',
            'scrapy.logformatter',
            'scrapy.extensions.*',
            'email.mime.*',
            '_cffi_backend',
            'setuptoolsm.pkg_resources'
            ]
packages = ['HospitalGenerator.models', 'HospitalGenerator.middlewares',
            'HospitalGenerator.pipelines', 'HospitalGenerator.progressbar',
            'HospitalGenerator.settings'
            ]
options = {"py2exe":
        {
            "includes":includes,
            "packages":packages,
        }
    }
setup(
    options=options,
    console=["HospitalGenerator/run.py"]
)
