# -*- coding: utf-8 -*-
import os
import sys
import logging 
import StringIO
from optparse import OptionParser
from lxml import etree
from datetime import datetime
from zeit.care import add_file_logging
import zeit.care.crawl
import zeit.connector.connector
from zeit.connector.resource import Resource
import zeit.connector.interfaces
import zope.authentication.interfaces
import zeit.connector.mock



class Ressortindexmanipulator(object):

    def __init__(self):
        self.months = {'01': 'Januar','02': 'Februar','03': u'März','04': 'April','05': 'Mai','06': 'Juni','07': 'Juli','08': 'August','09': 'September','10': 'Oktober','11': 'November','12': 'Dezember'}

        self.templatedir = os.path.dirname(__file__)+'/ressortindex_files/'
        self.templatedocs = [(f,self.templatedir+f) for f in os.listdir(self.templatedir) if os.path.isfile(self.templatedir+f)]
        #print self.templatedocs

    # Return a list with ressorts, months, years
    def get_ids(self,connector):
        ressorts = self.convert_ressortxmlfile_to_list(connector)
        months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        thisyear = int(datetime.today().strftime("%Y"))
        thismonth = str(datetime.today().strftime("%m"))
        id_infos = []
        for ressort in ressorts:
            year = 2010
            #while year <= thisyear:
            for year in range(year,thisyear+1):
                year_str = str(year)
                for month in months:
                    infos = []
                    infos.append('http://xml.zeit.de/'+ressort+'/'+year_str+'-'+month+'/index')
                    infos.append(year_str)
                    infos.append(month)
                    infos.append(ressort)
                    id_infos.append(infos)
                    #don't write index files for the future
                    if (year == thisyear) and (month == thismonth):
                        break
        return id_infos

    def convert_ressortxmlfile_to_list(self,connector):
        output = []
        xml = etree.parse(self.templatedir+'ressorts.xml')
        paths = xml.xpath('/ressortpfade/pfad')
        for path in paths:
            output.append(path.text)  
        return output

    def read_index_template_file(self, connector):
        resource = open(self.templatedir+'index')
        xml = resource.read()
        return xml

    def write_new_xml_from_template(self,templatexml,id):
        tree = etree.parse(StringIO.StringIO(templatexml))
        centerpage = tree.xpath('//centerpage')[0]
        # Elements which should be replaced
        attr_date_first_released = tree.xpath('//attribute[@name="date_first_released"]')[0]
        attr_ressort = tree.xpath('//attribute[@name="ressort"]')[0]
        attr_year = tree.xpath('//attribute[@name="year"]')[0]
        bodytitle = tree.xpath('//body/title')[0]
        teasertitle = tree.xpath('//teaser/title')[0]
        teasertext = tree.xpath('//teaser/text')[0]

        body = tree.xpath('//body')[0]
        teaser = tree.xpath('//teaser')[0]
        # Structure ids-variable: [[http://xml.zeit.de/<ressor>/<year>-<month>/index, <year>, <month>, <ressort>],...]
        year_string = id[1] 
        # Prepare variables
        month_string = self.months[id[2]] # '01' -> 'Januar'
        ressort_string = id[3][0].upper()+id[3][1:] # 'ressort' -> 'Ressort'
        # Replacing
        attr_date_first_released.text = datetime(int(id[1]), int(id[2]), 1, 0, 0, 0, microsecond=1).isoformat()+"+00:00"
        attr_ressort.text = ressort_string
        attr_year.text = year_string
        bodytitle.text = "Artikel und Nachrichten im "+month_string+" "+year_string+" aus dem Ressort "+ressort_string+" | ZEIT ONLINE"
        teasertitle.text = "Artikel und Nachrichten im "+month_string+" "+year_string+" aus dem Ressort "+ressort_string+" | ZEIT ONLINE"
        teasertext.text = "Lesen Sie alle Artikel und Nachrichten vom "+month_string+" "+year_string+" aus dem Ressort "+ressort_string+" auf ZEIT ONLINE"
        new_cp = etree.tostring(centerpage, encoding="UTF-8", xml_declaration=True)
        return centerpage 

    def insert_id_parameters_in_template(self, connector):  
        ids = self.get_ids(connector)
        templatexml = self.read_index_template_file(connector)

        for id in ids:
            new_xml = self.write_new_xml_from_template(templatexml,id)
            connector_id = id[0]
            new_resource = Resource(connector_id,
                'index',
                'centerpage',
                StringIO.StringIO(etree.tostring(new_xml, encoding="UTF-8", xml_declaration=True)),
                contentType = 'text/xml')
            connector[connector_id] = new_resource
        return connector

def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-c", "--collection", dest="collection",
                      help="entry collection for starting the indexfilewriting")
    parser.add_option("-w", "--webdav", dest="webdav",
                      help="webdav server uri")
    parser.add_option("-l", "--log", dest="logfile",
                      help="logfile for errors")
    parser.add_option("-f", "--force", action="store_true", dest="force",
                        help="no reinsurance question, for batch mode e.g.")

    (options, args) = parser.parse_args()

    if not options.collection:
        parser.error("missing entry point for indexfilewriting")

    if not options.webdav:
        parser.error("missing webdav uri")

    if options.logfile:
        add_file_logging(logger, options.logfile)
        
    if not options.force:
        user_ok = raw_input('\nWriting ressortindexfiles in webdav uri will start at %s.\nAre you sure? [y|n]: ' \
            % options.collection)
    else: 
        user_ok = "y" 
    
    if user_ok == "y":
       connector = zeit.connector.connector.Connector(roots=dict(
            default=options.webdav))
       insert_id_parameters_in_template(connector)
