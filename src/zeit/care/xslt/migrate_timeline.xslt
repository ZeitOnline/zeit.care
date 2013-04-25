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
   <xsl:template match="div[@class='inline-element timeline']">
      <timeline is_empty="false" publication-date="" expires="">
         <xsl:attribute name="href">
            <xsl:value-of select="./div[@class='href']/text()" />
         </xsl:attribute>
      </timeline>
   </xsl:template>

</xsl:stylesheet>

