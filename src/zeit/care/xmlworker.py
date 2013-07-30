# -*- coding: utf-8 -*-
import os
import sys
import logging
import StringIO
from optparse import OptionParser
from lxml import etree
from datetime import datetime
from zeit.care import add_file_logging
import zeit.connector.connector
import zeit.care.crawl
import zeit.care.publish
import zeit.care.worker
from zeit.connector.resource import Resource
import zeit.connector.interfaces
import zeit.connector.mock
import httplib
import urllib2
import re
#import zeit.cms.content.sources



logger_error_productid = logging.getLogger('error_productid')
logger_error_authorstarts = logging.getLogger('error_authorstarts')
logger_error_authorends = logging.getLogger('error_authorends')
logger_error_datefirst = logging.getLogger('error_date-first-released')
logger_error_datemodified = logging.getLogger('error_date-last-modified')
logger_error_semanticchange = logging.getLogger('error_last-semantic-change')
logger_error_modifiedsemantic = logging.getLogger('error_last-modified-semantic-change')
logger_info_zei = logging.getLogger('info_productid_zeit-print')
logger_info_zede = logging.getLogger('info_productid_zeit-online')
logger_info_zede_by_url = logging.getLogger('info_productid_zeit-online-per-url')
logger_info_tgs = logging.getLogger('info_productid_tagesspiegel')
logger_info_ztwi = logging.getLogger('info_productid_zeit-wissen')
logger_info_rele = logging.getLogger('info_date-first-released_attr-release')
logger_info_year_vol = logging.getLogger('info_date-first-released_year-volume')
logger_info_year_vol_copyr = logging.getLogger('info_date-first-released_year-volume-copyrights')
logger_info_date_copyr = logging.getLogger('info_date-first-released_date-copyrights')


logger_wrong_ressort = logging.getLogger('wrong-ressort')
logger_wrong_subressort = logging.getLogger('wrong-subressort')
logger_teaser_title_too = logging.getLogger('teaser-title-too')
logger_teaser_text_too = logging.getLogger('teaser-text-too')
logger_teaser_supertitle_too = logging.getLogger('teaser-supertitle-too')
logger_supertitle_too = logging.getLogger('supertitle-too')
logger_wrong_type = logging.getLogger('wrong-type')
logger_no_type = logging.getLogger('no-type')
logger_checkable = logging.getLogger('checkable')
logger_no_year = logging.getLogger('no-year')
logger_year_impossible = logging.getLogger('year-impossible')


publish = zeit.care.publish.publish_xmlrpc

wrong_ressort = []
wrong_subressort = []
no_year = []
year_impossible = []
no_ressort = 0

teaser_title_too = []
teaser_text_too = []
teaser_supertitle_too = []
supertitle_too = []

wrong_type = []
no_type = []
not_checkable = 0
checkable = []

validation_logger = False

class XmlWorker(object):

    def __init__(self):
        self.wrong_date_attr_to_delete = False

    def get_ressorts(self):
        tree = etree.parse(os.path.dirname(__file__)+'/xmlworker/navigation.xml')
        return tree

    def get_uris_from_file(self, path, string):
        links = []
        with open(path, 'r') as lines:
            for l in lines:
                lnk = l.replace("\n","")
                links.append(lnk.replace(string, 'http://xml.zeit.de'))
        lines.close()
        return links
   
    def _get_article(self, uri):
        try:
            res = urllib2.urlopen(uri)
            return res.read()
        except Exception, e:
            return False
        
    def _string_to_xml(self, article):
        tree = etree.parse(StringIO.StringIO(article))
        return tree
 
    def _xml_to_string(self, tree):
        return etree.tostring(tree, encoding="UTF-8", xml_declaration=True)

    def make_checkable(self,uri,connector):
        try:
            uri = unicode(uri.decode("utf8"))
            urgent = zeit.care.worker.get_property(connector[uri],'urgent','http://namespaces.zeit.de/CMS/workflow')
            edited = zeit.care.worker.get_property(connector[uri],'edited','http://namespaces.zeit.de/CMS/workflow')
            corrected = zeit.care.worker.get_property(connector[uri],'corrected','http://namespaces.zeit.de/CMS/workflow')
            #print urgent
            #print edited
            #print corrected

            if urgent is not None and urgent in 'yes' or (edited is not None and edited in 'yes' and corrected is not None and corrected in 'yes'):
                #print "checkable"
                global checkable
                if uri not in checkable:
                    checkable.append(uri)
                    logger_checkable.info(uri)
            else:
                #print "not_checkable"
                global not_checkable
                not_checkable += 1
                properties = {('urgent','http://namespaces.zeit.de/CMS/workflow'): 'yes'}
                crawler = zeit.care.crawl.ResourceProcess(uri,
                                                          connector,
                                                          zeit.care.worker.property_worker,
                                                          properties=properties,
                                                          publish=publish)
                #crawler.run()
                
        except Exception, e:
            return False
            

            
            #print "%s - Make checkable" % uri

    def create_year(self,uri):
        year = ''

        match = re.search(r"/[1-2][0,9][0-9][0-9]/", uri)
        if match:
            str = match.group(0)
            year = str.strip('/')
            return year

        date_first_released = zeit.care.worker.get_property(connector[uri],'date_first_released','http://namespaces.zeit.de/CMS/document')
        match = re.search(r"[1-2][0,9][0-9][0-9]", date_first_released)
        if match:
            year = match.group(0)
            return year


        copyrights = zeit.care.worker.get_property(connector[uri],'copyrights','http://namespaces.zeit.de/CMS/document')
        match = re.search(r"[1-2][0,9][0-9][0-9]", copyrights)
        if match:
            year = match.group(0)
            return year
        
        last_semantic_change = zeit.care.worker.get_property(connector[uri],'last-semantic-change','http://namespaces.zeit.de/CMS/document')
        match = re.search(r"[1-2][0,9][0-9][0-9]", last_semantic_change)
        if match:
            year = match.group(0)
            return year
            
        date_last_published = zeit.care.worker.get_property(connector[uri],'date_last_published','http://namespaces.zeit.de/CMS/workflow')
        match = re.search(r"[1-2][0,9][0-9][0-9]", date_last_published)
        if match:
            year = match.group(0)
            return year
            
        date_last_modified = zeit.care.worker.get_property(connector[uri],'date-last-modified','http://namespaces.zeit.de/CMS/document')            
        match = re.search(r"[1-2][0,9][0-9][0-9]", date_last_modified)
        if match:
            year = match.group(0)
            return year
        return False       
  

    def get_properties(self,uri,tree,ressorts,connector):
        uri = unicode(uri.decode("utf8"))
        try:
            type = zeit.care.worker.get_property(connector[uri],'type','http://namespaces.zeit.de/CMS/meta')
            #serie = zeit.cms.content.sources.SerieSource()
            ressort = zeit.care.worker.get_property(connector[uri],'ressort','http://namespaces.zeit.de/CMS/document')
            sub_ressort = zeit.care.worker.get_property(connector[uri],'sub_ressort','http://namespaces.zeit.de/CMS/document')
            print_ressort = zeit.care.worker.get_property(connector[uri],'ressort','http://namespaces.zeit.de/CMS/print')
            year = zeit.care.worker.get_property(connector[uri],'year','http://namespaces.zeit.de/CMS/document')       
    
            properties = {}
            if type is not None:
                if type not in 'article':
                    properties.update({('type','http://namespaces.zeit.de/CMS/workflow'): "yes"})
                    #print "%s - Type ungueltig: %s" % (uri,type)
                    global wrong_type
                    if uri not in wrong_type:
                        wrong_type.append(uri)
                        logger_wrong_type.info(uri)
            else:
                #print "Kein Type"
                global no_type
                if uri not in no_type:
                    no_type.append(uri)
                    logger_no_type.info(uri)
    
            if tree.xpath('//teaser/title'):
                teaser_title = tree.xpath('//teaser/title')[0]
                if len(teaser_title.text) > 70:
                    #print "%s - Teaser Titel zu lang" % uri
                    global teaser_title_too
                    if uri not in teaser_title_too:
                        teaser_title_too.append(uri)
                        logger_teaser_title_too.info(uri)
                   
            if tree.xpath('//teaser/text'):
                teaser_text = tree.xpath('//teaser/text')[0]
                if len(teaser_text.text) > 170:
                    #print "%s - Teaser Text zu lang" % uri
                    global teaser_text_too
                    if uri not in teaser_text_too:
                        teaser_text_too.append(uri)
                        logger_teaser_text_too.info(uri)
                
            if tree.xpath('//teaser/supertitle'):
                teaser_supertitle = tree.xpath('//teaser/supertitle')[0]
                if len(teaser_supertitle.text) > 70:
                    #print "%s - Teaser Supertitel zu lang" % uri
                    global teaser_supertitle_too
                    if uri not in teaser_supertitle_too:
                        teaser_supertitle_too.append(uri)
                        logger_teaser_supertitle_too.info(uri)
    
            if tree.xpath('//body/supertitle'):
                supertitle = tree.xpath('//body/supertitle')[0]
                if len(supertitle.text) > 70:
                    #print "%s - Teaser Supertitel zu lang" % uri
                    global supertitle_too
                    if uri not in supertitle_too:
                        supertitle_too.append(uri)
                        logger_supertitle_too.info(uri)
    
            if year is None or int(year) < 1900 or int(year) > 2100:
                year = self.create_year(uri)
                if year:
                    properties.update({('year','http://namespaces.zeit.de/CMS/document'): year})
                else:
                    global year_impossible
                    if uri not in year_impossible:
                        year_impossible.append(uri)
                        logger_year_impossible.info(uri)                    
                global no_year
                if uri not in no_year:
                    no_year.append(uri)
                    logger_no_year.info(uri)                
            
            if ressort is None:
                #print "%s - Kein Ressort" % uri
                global no_ressort
                no_ressort += 1
            else:             
                if ressorts.xpath('//ressort[@name="'+ressort+'"]'):              
                    pass
                else:
                    #print "%s - Ungueltiges Ressort: %s" % (uri,ressort)
                    global wrong_ressort
                    if ressort not in wrong_ressort:
                        wrong_ressort.append(ressort)
                        logger_wrong_ressort.info(ressort)
                    #else:
                    #    wrong_ressort[ressort].append(uri)
                        
                    
    
            if sub_ressort:
                if ressorts.xpath('//ressort[@name="'+ressort+'"]/subnavigation[@name="'+sub_ressort+'"]'):
                    pass
                else:
                    #print "%s - Ungueltiges Subressort: %s" % (uri,sub_ressort)
                    global wrong_subressort
                    if sub_ressort not in wrong_subressort:
                        wrong_subressort.append(sub_ressort)
                        logger_wrong_subressort.info(ressort + " -> " + sub_ressort)
                    #else:
                    #    wrong_subressort[sub_ressort].append(uri)                    
        except Exception, e:
            return False
        
    def _find_out_productid(self, tree, uri, connector):
        uri = unicode(uri.decode("utf8"))
        try:
            copyrights = zeit.care.worker.get_property(connector[uri],'copyrights','http://namespaces.zeit.de/CMS/document')
            #if tree.xpath('//attribute[@name="copyrights"]'):
            #    attr_copyrights = tree.xpath('//attribute[@name="copyrights"]')[0]
            #    copyrights = attr_copyrights.text
            if copyrights is not None and "DIE ZEIT" in copyrights.upper():
                logger_info_zei.info(uri)
                return "ZEI"
            elif copyrights is not None and "TAGESSPIEGEL" in copyrights.upper():
                logger_info_tgs.info(uri)
                return "TGS"
            elif copyrights is not None and  "ZEIT.DE" in copyrights.upper():
                logger_info_zede.info(uri)
                return "ZEDE"
            elif copyrights is not None and "ZEIT WISSEN" in copyrights.upper():
                logger_info_ztwi.info(uri)
                return "ZTWI"
            else:
                match = re.search(r"xml.zeit.de/online/[1-2][0-9][0-9][0-9]/[0-9][0-9]", uri)
                if match:
                    logger_info_zede_by_url.info(uri)
                    return "ZEDE"
                elif tree.xpath('//attribute[@name="volume"]') or tree.xpath('//attribute[@name="page"]'):
                    return "ZEI"
                else:
                    return False
        except Exception, e:
            return False

    def _create_date_first_released(self, tree, uri):
        year = ''
        volume = ''
        copyrights = ''

        if tree.xpath('//attribute[@name="date-first-release"]'):
            daterel = tree.xpath('//attribute[@name="date-first-release"]')[0]
            self.wrong_date_attr_to_delete = True
            logger_info_rele.info(uri)
            return daterel.text

        if tree.xpath('//attribute[@name="year"]') and tree.xpath('//attribute[@name="volume"]'):
            attr_year = tree.xpath('//attribute[@name="year"]')[0]
            attr_volume = tree.xpath('//attribute[@name="volume"]')[0]        
            
            if attr_year.text is not None and attr_year.text is not '' and attr_volume.text is not None and attr_volume.text is not '':
                volume = attr_volume.text
                year = attr_year.text
                logger_info_year_vol.info(uri)
                

        elif tree.xpath('//attribute[@name="copyrights"]'):
            attr_copyrights = tree.xpath('//attribute[@name="copyrights"]')[0]
            copyrights = attr_copyrights.text        

            match = re.search(r"[0-9][0-9]/[1-2][0-9][0-9][0-9]",copyrights)

            if match:
                dstr = match.group(0)
                dates = dstr.split("/")
                volume = dates[0]
                year = dates[1]
                logger_info_year_vol_copyr.info(uri)
            else:
                match = re.search(r"[0-2][0-9].[0-1][0-9].[1-2][0-9][0-9][0-9]",copyrights)
                
                if match:
                    dstr = match.group(0)
                    dates = dstr.split(".")
                    logger_info_date_copyr.info(uri)
                    return "%s-%s-%sT12:00:00Z" % (dates[2], dates[1], dates[0])
        else:
            return False         
        if year is not None and year is not '' and volume is not None and volume is not '':                    
            path_to_volume = "http://www.zeit.de/" + year + "/" + volume.zfill(2) + "/?re=false"
            res = self._get_article(path_to_volume)
            if res is not False:
                try:
                    tree = self._string_to_xml(res)
                except Exception, e:
                    return False
                daterel = False
                cnt = 0
                while daterel is False:
                    if tree.xpath('/page/body/cluster[@area="feature"]/region[@area="lead"]/container[@module="archive-print-volume"]/block/@href'):
                        volume_article_href = tree.xpath('/page/body/cluster[@area="feature"]/region[@area="lead"]/container[@module="archive-print-volume"]/block/@href')[cnt]
                    else:
                        return False
                    res = self._get_article(volume_article_href)
                    if res is not False:
                        try:
                            tree2 = self._string_to_xml(res)
                            if tree2.xpath('//attribute[@name="date_first_released"]'):
                                daterel = tree2.xpath('//attribute[@name="date_first_released"]')[0]
                        except Exception, e:
                            pass
                    cnt += 1
                return daterel.text
            else:
                return False
        else:
            return False


    def _detect_date_last_modified(self, tree):
        if tree.xpath('//attribute[@name="date_last_modified"]'):
            return True
        else:
            return False
 
        
    def _detect_last_semantic_change(self, tree):
        if not tree.xpath('//attribute[@name="last_semantic_change"]'):
            return False
        else:
            return True


    def _get_date_first_released(self, tree):
        if tree.xpath('//attribute[@name="date_first_released"]'):
            daterel = tree.xpath('//attribute[@name="date_first_released"]')[0]
            return daterel.text
        else:
            return False


#    def _insert_attribute(self, tree, var, val):
#        headlst = tree.find('head')
#        attr = etree.Element('attribute', name=var, ns="http://namespaces.zeit.de/CMS/workflow")
#        attr.text = val
#        tree.xpath('//article/head')[0].insert(0,attr)
#        return tree


#    def _delete_attribute(self, tree, var):
#        headlst = tree.find('head')
#        for child in headlst.iter():
#            attributes = child.attrib
#            if attributes.has_key('name'):
#                if attributes['name'] == var:
#                    headlst.remove(child)
#                    return tree

    
    def _delete_whitespace_author_begin(self, tree):
        attr_author = tree.xpath('//attribute[@name="author"]')[0]
        return attr_author.text[1:-1]
        
        
    def _delete_whitespace_author_end(self, tree):
        attr_author = tree.xpath('//attribute[@name="author"]')[0]
        if attr_author.text[-2:] == "  ":
            return attr_author.text[:-2]
        elif attr_author.text[-1:] == " ":
            return attr_author.text[:-1]
        else:
            return False
            
#    def write_file_on_dav(self, uri, xml,connector):
#        uri = uri.decode('utf-8')
#        filename = uri.split('/')[-1]
#        res = Resource(uri,
#            filename,
#            'article',
#            StringIO.StringIO(xml),
#            contentType = 'text/xml')
#        try:
#            connector[uri] = res
#        except httplib.HTTPException:
#            return False 
#        return connector

    def set_logger (self, logger, logfile):
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(logfile)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        
    def set_attribute_validation_logger(self,logpath):
        self.set_logger(logger_wrong_ressort, os.path.dirname(__file__) + "/../../../" + logpath + '/attributes_wrong_ressort.log')
        self.set_logger(logger_wrong_subressort, os.path.dirname(__file__) + "/../../../" + logpath + '/attributes_wrong_subressort.log')
        self.set_logger(logger_teaser_title_too, os.path.dirname(__file__) + "/../../../" + logpath + '/attributes_teaser_title.log')
        self.set_logger(logger_teaser_text_too, os.path.dirname(__file__) + "/../../../" + logpath + '/attributes_teaser_text.log')
        self.set_logger(logger_teaser_supertitle_too, os.path.dirname(__file__) + "/../../../" + logpath + '/attributes_teaser_supertitle.log')
        self.set_logger(logger_supertitle_too, os.path.dirname(__file__) + "/../../../" + logpath + '/attributes_supertitle.log') 
        self.set_logger(logger_wrong_type, os.path.dirname(__file__) + "/../../../" + logpath + '/attributes_wrong_type.log')
        self.set_logger(logger_no_type, os.path.dirname(__file__) + "/../../../" + logpath + '/attributes_no_type.log')
        self.set_logger(logger_checkable, os.path.dirname(__file__) + "/../../../" + logpath + '/attributes_checkable.log')
        self.set_logger(logger_no_year, os.path.dirname(__file__) + "/../../../" + logpath + '/attributes_no_year.log')
        self.set_logger(logger_year_impossible, os.path.dirname(__file__) + "/../../../" + logpath + '/attributes_year_impossible.log')     
    
    def run(self, path, logpath, string, connector, mode, logger):
        articles = self.get_uris_from_file(path, string)
        ressorts = self.get_ressorts()
        count = 0

        global validation_logger
        if validation_logger is False:
            self.set_attribute_validation_logger(logpath)
            validation_logger = True

              
        if mode == "productid":
            self.set_logger(logger_info_zei, os.path.dirname(__file__) + "/../../../" + logpath + '/info_productid_zeit-print.log')
            self.set_logger(logger_info_zede, os.path.dirname(__file__) + "/../../../" + logpath + '/info_productid_zeit-online.log')
            self.set_logger(logger_info_zede_by_url, os.path.dirname(__file__) + "/../../../" + logpath + '/info_productid_zeit-online-per-url.log')
            self.set_logger(logger_info_tgs, os.path.dirname(__file__) + "/../../../" + logpath + '/info_productid_tagesspiegel.log')
            self.set_logger(logger_info_ztwi, os.path.dirname(__file__) + "/../../../" + logpath + '/info_productid_zeit-wissen.log')
             
        elif mode == "datefirst":
            self.set_logger(logger_info_rele, os.path.dirname(__file__) + "/../../../" + logpath + '/info_date-first-released_attr-release.log')
            self.set_logger(logger_info_year_vol, os.path.dirname(__file__) + "/../../../" + logpath + '/info_date-first-released_year-volume.log')
            self.set_logger(logger_info_year_vol_copyr, os.path.dirname(__file__) + "/../../../" + logpath + '/info_date-first-released_year-volume-copyrights.log')
            self.set_logger(logger_info_date_copyr, os.path.dirname(__file__) + "/../../../" + logpath + '/info_date-first-released_date-copyrights.log')  
        
        for uri in articles:
            article = self._get_article(uri)
            if article is not False:
                tree = self._string_to_xml(article)
    
                # CASE - Product-Id
                if mode == "productid":
                    productid = self._find_out_productid(tree, uri, connector)
                    if productid is not False:
                        #http://namespaces.zeit.de/CMS/workflow urgent = yes
                        self.make_checkable(uri,connector)
                        self.get_properties(uri,tree,ressorts,connector)
                        
                        properties = {('product-id','http://namespaces.zeit.de/CMS/workflow'): productid}
                        properties.update({('urgent','http://namespaces.zeit.de/CMS/workflow'): "yes"})
                        try:
                            crawler = zeit.care.crawl.ResourceProcess(uri,
                                                                      connector,
                                                                      zeit.care.worker.property_worker,
                                                                      properties=properties,
                                                                      publish=publish)
                            #crawler.run()
                        except:
                            logger.error(uri+' Connector error. Perhaps no DB entry for article.')
                    else:
                        logger.error(uri+' Productid impossible to identify.')

                # CASE - Delete whitespace from authors begin
                elif mode == "authorstarts":
                    author = self._delete_whitespace_author_begin(tree)
                    if author is not False:
                        self.make_checkable(uri,connector)
                        self.get_properties(uri,tree,ressorts,connector)
                        properties = {('product-id','http://namespaces.zeit.de/CMS/document'): author}
                        properties.update({('urgent','http://namespaces.zeit.de/CMS/workflow'): "yes"})
                        try:
                            crawler = zeit.care.crawl.ResourceProcess(uri,
                                                                      connector,
                                                                      zeit.care.worker.property_worker,
                                                                      properties=properties,
                                                                      publish=publish)
                            #crawler.run()
                        except:
                            logger.error(uri+' Connector error. Perhaps no DB entry for article.')
                    else:
                        logger.error(uri+' Error while changing author string.')

                # CASE - Delete one or two whitespaces from authors end    
                elif mode == "authorends":
                    author = self._delete_whitespace_author_end(tree)
                    if author is not False:
                        self.make_checkable(uri,connector)
                        self.get_properties(uri,tree,ressorts,connector)
                        properties = {('product-id','http://namespaces.zeit.de/CMS/document'): author}
                        properties.update({('urgent','http://namespaces.zeit.de/CMS/workflow'): "yes"})
                        try:
                            crawler = zeit.care.crawl.ResourceProcess(uri,
                                                                      connector,
                                                                      zeit.care.worker.property_worker,
                                                                      properties=properties,
                                                                      publish=publish)
                            #crawler.run()
                        except:
                            logger.error(uri+' Connector error. Perhaps no DB entry for article.')
                    else:
                       logger.error(uri+' Error while changing author string.')
                        
                # CASE - Date first released    
                elif mode == "datefirst":
                    self.wrong_date_attr_to_delete = False
                    datefirstrel = self._create_date_first_released(tree, uri)
                    if datefirstrel is not False:
                        self.make_checkable(uri,connector)
                        self.get_properties(uri,tree,ressorts,connector)
                        properties = {('date_first_released','http://namespaces.zeit.de/CMS/document'): datefirstrel}
                        properties.update({('urgent','http://namespaces.zeit.de/CMS/workflow'): "yes"})
                        #if self.wrong_date_attr_to_delete is True:
                            # Perhaps not necessary
                        if self._detect_date_last_modified(tree) is False:
                            properties.update({('date_last_modified','http://namespaces.zeit.de/CMS/document'): datefirstrel})
                        if self._detect_last_semantic_change(tree) is False:
                            properties.update({('last_semantic_change','http://namespaces.zeit.de/CMS/document'): datefirstrel})
                        try:
                            crawler = zeit.care.crawl.ResourceProcess(uri,
                                                                      connector,
                                                                      zeit.care.worker.property_worker,
                                                                      properties=properties,
                                                                      publish=publish)
                            #crawler.run()
                        except:
                            logger.error(uri+' Connector error. Perhaps no DB entry for article.')

                    else:
                        logger.error(uri+' Could not create date_first_released.')
 
                # CASE - Date last modified
                elif mode == "datemodified":
                    datefirstrel = self._create_date_first_released(tree, uri)
                    if datefirstrel is not False:
                        self.make_checkable(uri,connector)
                        self.get_properties(uri,tree,ressorts,connector)
                        properties = {('date_last_modified','http://namespaces.zeit.de/CMS/document'): datefirstrel}
                        properties.update({('urgent','http://namespaces.zeit.de/CMS/workflow'): "yes"})
                        try:
                            crawler = zeit.care.crawl.ResourceProcess(uri,
                                                                      connector,
                                                                      zeit.care.worker.property_worker,
                                                                      properties=properties,
                                                                      publish=publish)
                            #crawler.run()
                        except:
                            logger.error(uri+' Connector error. Perhaps no DB entry for article.')
                    else:
                        logger.error(uri+' Could not get date_first_released.')
                        
                # CASE - Last semantic change    
                elif mode == "semanticchange":
                    datefirstrel = self._get_date_first_released(tree)
                    if datefirstrel is not False:
                        self.make_checkable(uri,connector)
                        self.get_properties(uri,tree,ressorts,connector)
                        properties = {('last_semantic_change','http://namespaces.zeit.de/CMS/document'): datefirstrel}
                        properties.update({('urgent','http://namespaces.zeit.de/CMS/workflow'): "yes"})
                        try:
                            crawler = zeit.care.crawl.ResourceProcess(uri,
                                                                      connector,
                                                                      zeit.care.worker.property_worker,
                                                                      properties=properties,
                                                                      publish=publish)
                            #crawler.run()
                        except:
                            logger.error(uri+' Connector error. Perhaps no DB entry for article.')
                    else:
                        logger.error(uri+' Could not get date_first_released.')
                                        
                # CASE - Date last modified and last semantic change    
                elif mode == "modifiedsemantic":
                    datefirstrel = self._get_date_first_released(tree)
                    if datefirstrel is not False:
                        self.make_checkable(uri,connector)
                        self.get_properties(uri,tree,ressorts,connector)
                        properties = {('date_last_modified','http://namespaces.zeit.de/CMS/document'): datefirstrel,
                                      ('last_semantic_change','http://namespaces.zeit.de/CMS/document'): datefirstrel}
                        properties.update({('urgent','http://namespaces.zeit.de/CMS/workflow'): "yes"})
                        try:
                            crawler = zeit.care.crawl.ResourceProcess(uri,
                                                                      connector,
                                                                      zeit.care.worker.property_worker,
                                                                      properties=properties,
                                                                      publish=publish)
                            #crawler.run()
                        except:
                            logger.error(uri+' Connector error. Perhaps no DB entry for article.')
                    else:
                        logger.error(uri+' Could not get date_first_released.')

            else:
                logger.error(uri + " Could not get article from uri")                

         
            #print uri
            count += 1
            '''if count % 100 == 0:
                print "Ressorts:"
                print wrong_ressort
                print "\n"
                
                print "Subressorts:"
                print wrong_subressort
                print "\n"       
        
                print "Kein Jahr:"
                print no_year
                print "\n" 
        
                print "Kein Ressort:"
                print no_ressort
                print "\n"
        
                print "Teaser Titel zu lang:"
                print teaser_title_too
                print "\n"
        
                print "Teaser Text zu lang:"
                print teaser_text_too
                print "\n"
                
                print "Teaser Supertitle zu lang:"
                print teaser_supertitle_too
                print "\n"
        
                print "Supertitle zu lang:"
                print supertitle_too
                print "\n"       
        
                print "Kein type:"
                print no_type
                print "\n"
                
                print "Falscher type:"
                print wrong_type
                print "\n"
        
                print "Checkable:"
                print checkable
                print "\n"
        
                print "Not checkable:"
                print not_checkable
                print "\n"'''
            #if count > 1000:
            #    break
        print "Ressorts:"
        print wrong_ressort
        print "\n"
        
        print "Subressorts:"
        print wrong_subressort
        print "\n"       

        print "Kein Jahr:"
        print no_year
        print "\n" 

        print "Jahr nicht möglich:"
        print year_impossible
        print "\n"

        print "Kein Ressort:"
        print no_ressort
        print "\n"

        print "Teaser Titel zu lang:"
        print teaser_title_too
        print "\n"

        print "Teaser Text zu lang:"
        print teaser_text_too
        print "\n"
        
        print "Teaser Supertitle zu lang:"
        print teaser_supertitle_too
        print "\n"

        print "Supertitle zu lang:"
        print supertitle_too
        print "\n"       

        print "Kein type:"
        print no_type
        print "\n"
        
        print "Falscher type:"
        print wrong_type
        print "\n"

        print "Checkable:"
        print checkable
        print "\n"

        print "Not checkable:"
        print not_checkable
        print "\n"
               
        #return count

def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-p", "--path", dest="path",
                        help="Relative path to files directory")
    parser.add_option("-w", "--webdav", dest="webdav",
                        help="webdav server uri")
    parser.add_option("-s", "--string", dest="string",
                        help="string which would be replaced by http://xml.zeit.de")
    parser.add_option("-l", "--log", dest="logpath",
                        help="Relative path to directory for logfiles, infos and errors")
    parser.add_option("-f", "--force", action="store_true", dest="force",
                        help="no reinsurance question, for batch mode e.g.")
    
    (options, args) = parser.parse_args()

    path_productid = False
    path_author_starts = False
    path_author_ends = False
    path_date_first = False
    path_date_modified = False
    path_semantic_change = False
    path_modified_semantic = False
    
    message = ""

    if os.path.isfile(options.path + "/missing_productid.txt"):
        message  += '\nmissing_productid.txt - Will process articles and insert to them a product id'
        path_productid = options.path + "/missing_productid.txt"
        
    if os.path.isfile(options.path + "/author_starts.txt"):
        message += '\nauthor_starts.txt - Will delete whitespace from the authors begin'
        path_author_starts = options.path + "/author_starts.txt"
        
    if os.path.isfile(options.path + "/author_ends.txt"):
        message += '\nauthor_ends.txt - Will delete whitespace from the authors end'
        path_author_ends = options.path + "/author_ends.txt"
        
    if os.path.isfile(options.path + "/date_first_released.txt"):
        message += '\ndate_first_released.txt - Will add missing attribute date_first_released'
        path_date_first = options.path + "/date_first_released.txt"
        
    if os.path.isfile(options.path + "/date_last_modified.txt"):
        message += '\ndate_last_modified.txt - Will add missing attribute date_last_modified'
        path_date_modified = options.path + "/date_last_modified.txt" 

    if os.path.isfile(options.path + "/last_semantic_change.txt"):
        message += '\nlast_sematic_change.txt - Will add missing attribute last_semantic_change'
        path_semantic_change = options.path + "/last_semantic_change.txt"

    if os.path.isfile(options.path + "/last_modified_semantic_change.txt"):
        message += '\nlast_modified_sematic_change.txt - Will add missing attribute date_last_modified together with last_semantic_change'
        path_modified_semantic = options.path + "/last_modified_semantic_change.txt"

    if not options.path:
        parser.error("missing path to files")

    if not options.string:
        parser.error("missing string to replace")
    
    if not options.webdav:
        parser.error("missing webdav uri")
    
    if not os.path.exists(options.logpath):
        parser.error("missing path for logfiles")
            
    if not options.force:
        user_ok = raw_input('\nFound the following files in %s and will do the listed actions: \n%s\n\nAre you sure? [y|n]: ' \
            % (options.path, message))
    else: 
        user_ok = "y" 
        
    if user_ok == "y":

        connector = zeit.connector.connector.Connector(roots=dict(
            default=options.webdav))

        # Process missing_productid.txt
        if path_productid is not False:
            #logger_productid_error = logging.getLogger('error_productid')
            add_file_logging(logger_error_productid, os.path.dirname(__file__) + "/../../../" + options.logpath + '/error_productid.log')
            injectids = XmlWorker()
            injectids.run(path_productid, options.logpath, options.string, connector, 'productid', logger_error_productid)
            
        # Process author_starts.txt
        if path_author_starts is not False:
            #logger_error_authorstarts = logging.getLogger('error_authorstarts')
            add_file_logging(logger_error_authorstarts, os.path.dirname(__file__) + "/../../../" + options.logpath + '/error_authorstarts.log')
            authorstarts = XmlWorker()
            authorstarts.run(path_author_starts, options.logpath, options.string, connector, 'authorstarts', logger_error_authorstarts)
        
        # Process author_ends.txt
        if path_author_ends is not False:
            #logger_error_authorends = logging.getLogger('error_authorends')
            add_file_logging(logger_error_authorends, os.path.dirname(__file__) + "/../../../" + options.logpath + '/error_authorends.log')
            authorends = XmlWorker()
            authorends.run(path_author_ends, options.logpath, options.string, connector, 'authorends', logger_error_authorends)

        # Process date_first_released.txt
        if path_date_first is not False:
            #logger_error_datefirst = logging.getLogger('error_date-first-released')
            add_file_logging(logger_error_datefirst, os.path.dirname(__file__) + "/../../../" + options.logpath + '/error_date-first-released.log')
            datefirst = XmlWorker()
            datefirst.run(path_date_first, options.logpath, options.string, connector, 'datefirst', logger_error_datefirst) 

        # Process date_last_modified.txt
        if path_date_modified is not False:
            #logger_error_datefirst = logging.getLogger('error_date-first-released')
            add_file_logging(logger_error_datemodified, os.path.dirname(__file__) + "/../../../" + options.logpath + '/error_date-last-modified.log')
            datemodified = XmlWorker()
            datemodified.run(path_date_modified, options.logpath, options.string, connector, 'datemodified', logger_error_datemodified)
            
        # Process last_semantic_change.txt
        if path_semantic_change is not False:
            #logger_error_datefirst = logging.getLogger('error_date-first-released')
            add_file_logging(logger_error_semanticchange, os.path.dirname(__file__) + "/../../../" + options.logpath + '/error_last-semantic-change.log')
            semantic = XmlWorker()
            semantic.run(path_semantic_change, options.logpath, options.string, connector, 'semanticchange', logger_error_semanticchange)

        # Process last_modified_semantic_change.txt
        if path_modified_semantic is not False:
            #logger_error_datefirst = logging.getLogger('error_date-first-released')
            add_file_logging(logger_error_modifiedsemantic, os.path.dirname(__file__) + "/../../../" + options.logpath + '/error_last-modified-semantic-change.log')
            modifiedsemantic = XmlWorker()
            modifiedsemantic.run(path_modified_semantic, options.logpath, options.string, connector, 'modifiedsemantic', logger_error_modifiedsemantic)            
       
