'''
Created on 2016/1/7

@author: K.Yao
'''


from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from selenium import webdriver
import os
import time
import webbrowser
import re
import csv

from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO
class Website():
    def __init__(self, url):
        self.__url = url # save root url
        self.__soup = self.__getSoup()
        
        #variables for searching for premium (function:getPremium)
        self.__currentSoup = None
        self.__interalurl = set()
        self.__interalTargetTag = set()
        self.__exteralTargetTag = set()
        
        
    def getPremium(self):
        '''
        This function basically gets target urls and extract the data from the urls 
        you found.
        '''
        #first get the url that may contain the data that you want.
        self.getTargeturl()
        
        #debug code, examine the target url.
#         print('------------------------->internal_target')
# #         add filtered tag to target set
#         for tag in self.__interalTargetTag:
#             print(tag)        
#           
#         print('------------------------->external_target')
#         for tag in self.__exteralTargetTag:
#             print(tag)        
         
        #Then extract data from the target url
        targetData = self.getTargetData()
        result = 0
        for v in targetData:
            if v > result:
                result = v
        return result

    def getTargeturl(self, rel_url = '', abs_url = ''):
        '''
        if abs_url exists, it will use that to get current soup.
        if it doesn't exist, it will use rel_url to get current soup.
        1. set current page and then get all internal Links and external links
        2. store target tags(internal/external) to __interalTargetTag and __exteralTargetTag
        3. filter target tags with keywords.
        4. do this recursively with all the pages in this website.
        '''
        self.__currentSoup = self.__getSoup(rel_url, abs_url)
        #if current url is not accessible stop recurrence
        if not self.__currentSoup:
            return
        
        # first get all internal and external tags and links on current page
        cur_inter_tag = self.getInternalLinks()
        cur_exter_tag = self.getExternalLinks()
        #caution: add all the internal url to internalurl set before filter because you are not going to
        #filter internal links that you want to search recursively.
        self.__interalurl = self.__interalurl.union({tag.attrs['href']for tag in cur_inter_tag})
        #add target tag to their tag sets
        self.__interalTargetTag = self.__interalTargetTag.union(cur_inter_tag)
        self.__exteralTargetTag = self.__exteralTargetTag.union(cur_exter_tag)
        #filter all the tags with keywords 
        cur_inter_tag = {tag for tag in cur_inter_tag if 
                            re.search('annual.*?report|press.*?release|about|investor', tag.attrs['href'], re.IGNORECASE) or 
                            re.search('annual.*?report|press.*?release|about|investor', str(tag.get_text().strip()), re.IGNORECASE)}
        self.__interalTargetTag = {tag for tag in self.__interalTargetTag if 
                            re.search('annual.*?report|press.*?release|about|investor', tag.attrs['href'], re.IGNORECASE) or 
                            re.search('annual.*?report|press.*?release|about|investor', str(tag.get_text().strip()), re.IGNORECASE)}
        self.__exteralTargetTag = {tag for tag in self.__exteralTargetTag if 
                            re.search('annual.*?report|press.*?release|about|investor', tag.attrs['href'], re.IGNORECASE) or 
                            re.search('annual.*?report|press.*?release|about|investor', str(tag.get_text().strip()), re.IGNORECASE)}        
        #search all the internal set recursively 
        for tag in cur_inter_tag:
            if re.search('^(http|www)', tag.attrs['href'], re.IGNORECASE):
                self.getTargeturl(abs_url = tag.attrs['href']) #this is internel link but have http://, so don't add root
            else:
                self.getTargeturl(tag.attrs['href'])

    
    def getInternalLinks(self):
        '''
        Get all the internal links in current page.
        '''
        internalTag = set()
        for tag in self.__currentSoup.find_all('a', {'href': re.compile('^(/|.*' + self.extractRooturl() + ')')}): #include root url
            if tag.attrs['href'] not in self.__interalurl:
                internalTag.add(tag)

        return internalTag
            
    def getExternalLinks(self):
        '''
        Get all the external links in current page.
        '''
        externalTag = set()
        for tag in self.__currentSoup.find_all('a', {'href': re.compile('^(http|www|//)((?!' + self.extractRooturl() + ').)*$')}): #exclude root url
            if tag not in self.__exteralTargetTag:
                externalTag.add(tag)
        return externalTag
    
    
    @staticmethod
    def readPDF(pdfFile):
        '''
        @pdfFile the file with type of pdf.
        @return: strings in this pdf.
        '''
        pass
        try:
            rsrcmgr = PDFResourceManager()
            retstr = StringIO()
            laparams = LAParams()
            device = TextConverter(rsrcmgr, retstr, laparams=laparams)
            process_pdf(rsrcmgr, device, pdfFile)
            device.close()
            content = retstr.getvalue()
            retstr.close()
        except AttributeError as e:
            print(e)
            return None
        return content    
    
    @staticmethod
    def getpdfFile(url):
        '''
        @url url must a pdf file.
        @return: file with type of pdf
        '''
        if not re.match('^http', url, re.IGNORECASE):
            url = url.replace('//', 'https://')
        try:
            pdfFile = urlopen(url)
        except HTTPError as e:
            print(e)
            return None
        except ValueError as e:
            print(e)
            return None
        except URLError as e:
            print(e)
            return None
        return pdfFile
    
    
    def getTargetData(self):
        '''
        1. Do some changes with interanl url and external url.
        2. convert external pdfs to strings and find data with regular expression. 
        if the data is not empty, return the result.
        3. convert internal pdfs to strings and find data with regular expression.
        '''
        #at this point we should have all the target tag(url) in this website, all we need 
        #to do is to search each page's table and search pdf for target data.
        targetpdf_internal = {re.sub('https?://|www.' + self.extractRooturl(), '', tag.attrs['href']) for tag in self.__interalTargetTag if re.search('.*\.pdf', tag.attrs['href'], re.IGNORECASE)}
        targetpdf_external = {tag.attrs['href'] for tag in self.__exteralTargetTag if re.search('.*\.pdf', tag.attrs['href'], re.IGNORECASE)}
        # add internal root url
        targetpdf_internal = [re.sub('^/(?!/)', self.__url, url)  for url in targetpdf_internal]
        
        #debug code print out target pdf url
        print('------------------------->internal_target')
        for url in targetpdf_internal:
            print(url)
            
        print('------------------------->external_target')
        for url in targetpdf_external:
            print(url)
        
        resultList = []
        for url in targetpdf_external:
            pdfFile = Website.getpdfFile(url)
            if not pdfFile:
                continue
            outputString = Website.readPDF(pdfFile)
            if not outputString:
                continue
            
            #process result by using regular expression
            resultList_ex = []
            for premium in re.findall(r'(premium[s]? written|written premium[s]?)[\s\S]{0,500}?(\d+(,\d+)+)([\s\S]{1,60}(\d{3}(,\d+)+))?([\s\S]{1,275}(\d,\d{3},(\d+)+))?', outputString, re.IGNORECASE):
                if len(premium[1])> 2 :
                    resultList_ex.append(int(premium[1].replace(',', '')))
                if len(premium[4])> 2 :
                    resultList_ex.append(int(premium[4].replace(',', '')))
                if len(premium[7])> 2 :
                    resultList_ex.append(int(premium[7].replace(',', '')))
            resultList.extend(resultList_ex)
        if resultList:
            return resultList
        for url in targetpdf_internal:
            pdfFile = Website.getpdfFile(url)
            if not pdfFile:
                continue
            outputString = Website.readPDF(pdfFile)
            if not outputString:
                continue
            resultList_in = []
            for premium in re.findall(r'(premium[s]? written|written premium[s]?)[\s\S]{0,500}?(\d+(,\d+)+)([\s\S]{1,60}(\d{3}(,\d+)+))?([\s\S]{1,275}(\d,\d{3},(\d+)+))?', outputString, re.IGNORECASE):
                if len(premium[1])> 2 :
                    resultList_in.append(int(premium[1].replace(',', '')))
                if len(premium[4])> 2 :
                    resultList_in.append(int(premium[4].replace(',', '')))
                if len(premium[7])> 2 :
                    resultList_in.append(int(premium[7].replace(',', '')))
            resultList.extend(resultList_in)
            if resultList:
                return resultList
#             print(url,'\n' + url_ex)
        return resultList
        
        
    
    def extractRooturl(self):
        '''
        e.g.: get google.com part of https://www.google.com/
        '''
        url = re.sub('http://|www.', '', self.__url)
        addressParts = url.split("/")
        return addressParts[0]
    
      
    def __getSoup(self, rel_url = '', abs_url = ''):
        '''
        Get Soup object of the url you specified.
        if abs_url exists, it will use that to get current soup.
        if it doesn't exist, it will use rel_url to get current soup.
        handle all kinds of errors.
        '''
        
        #eliminate escape characters content with UTF-8
        rel_url = bytes(rel_url, 'UTF-8')
        rel_url = rel_url.decode('ascii', 'ignore')
        abs_url = bytes(abs_url, 'UTF-8')
        abs_url = abs_url.decode('ascii', 'ignore')
        
        try:
            if abs_url:
                conn = urlopen(abs_url)
            else:
                conn = urlopen(self.__url + rel_url)
        except HTTPError as e: 
            # Server thinks this is a bot. so we use real broswer to access it!
            driver = webdriver.PhantomJS(executable_path = os.getcwd() + '\phantomjs.exe')
            if abs_url:
                driver.get(abs_url)
            else:
                driver.get(self.__url + rel_url)
            time.sleep(1) # wait for JavaScript executing
            soup = BeautifulSoup(driver.page_source, "html.parser")
            driver.close()
            return soup
        except URLError as e:
            print(e, self.__url + rel_url)
            return None
        except ConnectionError as e:
            print(e)
            return None
        
        try:
            soup = BeautifulSoup(conn.read(), "html.parser")
            
        except AttributeError as e:
            print(e, self.__url + rel_url)
            return None
        finally:
            conn.close()
        
        #if this site content meta redirect, attach new url to root url and reopen it.
        #eg. <meta content="1; URL=/aegislink.html" http-equiv="Refresh">
        redirectTag = soup.find('meta', {'content' : re.compile('url=', re.IGNORECASE), 'http-equiv' : re.compile('Refresh', re.IGNORECASE)} )
        if redirectTag:
            m = re.search(r'url=/(.*)', redirectTag.attrs['content'], re.IGNORECASE)
            return self.__getSoup(self.__url + m.group(1))

        # <link href="http://www.acegroup.com" rel="canonical"/>
        # if this site use link to redirect url to real one, we have to recognize it
        linkTag = soup.find('link', {'rel' : re.compile('canonical', re.IGNORECASE)} )
        if linkTag and linkTag.attrs['href']:
            self.__url = linkTag.attrs['href']
            try:
                if abs_url:
                    conn = urlopen(abs_url)
                else:
                    conn = urlopen(self.__url + rel_url)
            except HTTPError as e: 
                # Server thinks this is a bot. so we use real broswer to access it!
                driver = webdriver.PhantomJS(executable_path = os.getcwd() + '\phantomjs.exe')
                if abs_url:
                    driver.get(abs_url)
                else:
                    driver.get(self.__url + rel_url)
                time.sleep(1) # wait for JavaScript executing
                soup = BeautifulSoup(driver.page_source, "html.parser")
                driver.close()
                return soup
            except URLError as e:
                print(e, self.__url + rel_url)
                return None
            try:
                soup = BeautifulSoup(conn.read(), "html.parser")
                
            except AttributeError as e:
                print(e, self.__url + rel_url)
                return None
            finally:
                conn.close()
        return soup
    
    
    
    
    
    
    def getTitle(self):
        try:
            title = self.__soup.title.get_text().strip()
        except AttributeError:
            return None
        return title

    def openSite(self, rel_url = ''):
        webbrowser.open(self.__url + rel_url)
     
#debug code: store strings of one pdf file to a txt file.
# pdfFile = Website.getpdfFile('http://s1.q4cdn.com/131015182/files/doc_financials/annual/AIZ_Assurant_AR_2014_v003_f3s0s9.pdf')
# outputString = Website.readPDF(pdfFile)
# print(outputString)
# fout = open('../result3.txt', 'wt',encoding = 'utf-8')
# fout.write(outputString)
# fout.close()

with open('list_of_url.csv', 'rt') as urlFile:
    csvReader = csv.reader(urlFile)
    #                                                  stop when shortest sequence is done
    siteList = [ Website(url[0].strip())  for url,i in zip(csvReader, range(20)) if url[0].strip()]
    for site in siteList:
        print(site.getTitle())
        print('premium', site.getPremium())
         
         
    