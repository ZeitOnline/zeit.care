from setuptools import setup, find_packages

setup(
    name='zeit.care',
    version='0.3.dev0',
    author='Christian Zagrodnick, Ron Drongowski, Dominik Hoppe',
    author_email='cz@gocept.com',
    url='http://trac.gocept.com/zeit',
    description="""\
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='gocept proprietary',
    namespace_packages = ['zeit'],
    install_requires=[
        'zeit.connector',
        'setuptools',
        'pytz',
        ],
    entry_points = """
        [console_scripts]  
        isofication = zeit.care.worker:isofy_main
        xslt = zeit.care.worker:xslt_main
        divisor = zeit.care.divisor:main
        boxinjector = zeit.care.boxinjector:main
        ressortindexwriter = zeit.care.ressortindex:main
        commentthreadworker = zeit.care.commentthread:main
        propertyworker = zeit.care.worker:property_main
        xmlworker = zeit.care.xmlworker:main
        """
)
