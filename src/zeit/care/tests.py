from zope.testing import doctest


def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        'date_test.txt',
        'divisor.txt',
        'boxinjector.txt',
        'ressortindex.txt',
        'xmlworker.txt',
        'xmlworker2.txt',
        optionflags=doctest.ELLIPSIS
    )
