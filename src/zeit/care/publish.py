import xmlrpclib
import time

s = xmlrpclib.ServerProxy('http://system.newspublish:TWV$xSUz@vivi.zeit.de/')


def publish_xmlrpc(uri):
    try:
        if (s.can_publish(uri)):
            s.publish(uri)
            print("publish " + uri)
            time.sleep(8)
        else:
            print("cannot publish " + uri)
    except:
        print("problems " + uri)
