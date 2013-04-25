<?xml version='1.0'?>
<xsl:stylesheet version="1.0" 
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:zeit="http://namespaces.zeit.de/CMS/XSLT/functions"
                xmlns:py="http://codespeak.net/lxml/objectify/pytype"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                exclude-result-prefixes="py xsi"
                extension-element-prefixes="zeit">

   <xsl:output method='xml'
               encoding='utf-8'/>

   <xsl:template match="@*|node()">
      <xsl:copy>
         <xsl:apply-templates select="*|@*|text()"/>
      </xsl:copy>
   </xsl:template>

   <xsl:template match="body//relateds" />

</xsl:stylesheet>

