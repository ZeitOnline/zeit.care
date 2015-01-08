from setuptools import setup, find_packages


setup(
    name='zeit.care',
    version='0.3.dev0',
    author='gocept, Zeit Online',
    author_email='zon-backend@zeit.de',
    url='http://www.zeit.de/',
    description="Helper scripts for managing DAV content",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    namespace_packages=['zeit'],
    install_requires=[
        'zeit.connector',
        'setuptools',
        'pytz',
    ],
    entry_points="""
        [console_scripts]
        isofication=zeit.care.worker:isofy_main
        xslt=zeit.care.worker:xslt_main
        divisor=zeit.care.divisor:main
        boxinjector=zeit.care.boxinjector:main
        ressortindexwriter=zeit.care.ressortindex:main
        commentthreadworker=zeit.care.commentthread:main
        propertyworker=zeit.care.worker:property_main
        xmlworker=zeit.care.xmlworker:main
        """
)
