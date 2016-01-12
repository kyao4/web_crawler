'''
Created on 2016/1/7

@author: K.Yao
'''
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import re
import random
import csv
import os
import webbrowser

class Website():
    def __init__(self, url):
        self.__url = url # save root url
        self.__soup = self.__getSoup()
        self.__siteMap = set()
       
        
        
    
    def __getSoup(self, rel_url = ''):
        try:
            conn = urlopen(self.__url + rel_url)
        except HTTPError as e:
            print(e)
            return None
        try:
            soup = BeautifulSoup(conn.read())
        except AttributeError as e:
            print(e)
            return None
        return soup
    
    
    def getSiteMap(self, relativeurl = ''):
        soup = self.__getSoup(relativeurl)
        if soup == None:
            return
        try:
            title = soup.h1.get_text()
            p = soup.find('', {'id': 'mw-content-text'}).find('p').get_text()
            href = soup.find('', {'id': 'ca-edit'}).find('span').find('a').attrs['href']
            self.__list.append(title)
            self.__list.append(p)
            self.__list.append(href)
            print(title)
            print(p)
            print(href)
            if not os.path.exists('../files/'):
                os.makedirs('../files/')
            csvFile = open('../files/editors.csv', 'at', encoding='utf-8')
            writer = csv.writer(csvFile)
            try:
                writer.writerow(self.__list)
            finally:
                csvFile.close()
                
        except AttributeError:
            pass
        try:
            links = soup.body.find_all('a', {'href': re.compile('^(/wiki/)((?!:).)*$')})
        except AttributeError:
            return
        for link in links:
            if link.attrs['href'] not in self.__siteMap:
                newPage = link.attrs['href']
                self.__list = []
                self.__list.append(newPage)
                self.__siteMap.add(newPage)
                print('\n------------->' + newPage)
                self.getSiteMap(newPage)
    
    
    def getTitle(self):
        '''
        return title of a page, if there is no title in this
        page return None
        '''
        try:
            title = self.__soup.title.get_text()
        except AttributeError:
            return None
        return title
    
    def getallLinks(self):
        return self.__soup.body.find_all('a', {'href' : re.compile('^(/wiki/)((?!:).)*$')})
        
    def getallLinksByURL(self, relativeurl):
        try:
            conn = urlopen(self.__url + relativeurl)
        except HTTPError as e:
            print(e)
            return None
        try:
            soup =  BeautifulSoup(conn.read())
            links = soup.body.find_all('a', {'href' : re.compile('^(/wiki/)((?!:).)*$')})
        except AttributeError as e:
            print(e)
            return None
        return links
    
    def sixDegree(self, relativeurl):
        links = self.getallLinksByURL(relativeurl)
        while links:
            nextLink = links[random.randint(0, len(links) - 1)].attrs['href']
            print(nextLink)
            links = self.getallLinksByURL(nextLink)
            
    def getHTML(self):
        '''
        If return None, There are errors in URL
        '''
        try:
            HTML = self.__soup.prettify()
        except AttributeError:
            return None
        return HTML
    
    def getRedTag(self):
        for span in self.__soup.find_all('span', {'class':'red'}):
            print(span.get_text())
            
    def getH1H2(self):
        for head in self.__soup.find_all(['h1', 'h2']):
            print(head.get_text())
            
    def getTableChildren(self):
        for child in self.__soup.find('table', {'id':'giftList'}).descendants:
            print(child)
            
    def getTableDataRow(self):
        for row in self.__soup.find('table', {'id':'giftList'}).tr.next_siblings:
            print(row)
    
    def getImagePrice(self):
        print(self.__soup.find('img', {'src': '../img/gifts/img1.jpg'}).parent.previous_sibling.get_text())
    
    def getImagebyRE(self):
        for img in self.__soup.find_all('img', {'src': re.compile("\.\.\/img\/gifts/img.*\.jpg")}):
            print(img)
    @staticmethod        
    def openCSV(url, path):
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            return None
        file = open(path, 'rt', encoding = 'utf-8')
        CSVReader = csv.reader(file)
        for row in CSVReader:
            if row:
                webbrowser.open(url + row[0])
            
url = 'https://en.wikipedia.org'
site = Website(url)
print(site.getTitle())

# for link in site.getallLinks():
#     print(link.attrs['href'])

# site.sixDegree('/wiki/Kevin_Bacon')

site.getSiteMap()
# Website.openCSV(url, '../files/editors.csv')
#open csv and open links


# from pdfminer.pdfinterp import PDFResourceManager, process_pdf
# from pdfminer.converter import TextConverter
# from pdfminer.layout import LAParams
# from io import StringIO
# from io import open
# 
# 
# def readPDF(pdfFile):
#     rsrcmgr = PDFResourceManager()
#     retstr = StringIO()
#     laparams = LAParams()
#     device = TextConverter(rsrcmgr, retstr, laparams=laparams)
#     process_pdf(rsrcmgr, device, pdfFile)
#     device.close()
#     content = retstr.getvalue()
#     retstr.close()
#     return content


# pdfFile = urlopen("http://fls.arbella.com/communications/451683.Arbella.webready.pdf");
# outputString = readPDF(pdfFile)
# result = re.findall('premium[\s\S]*?(\d+(,\d+)+)', outputString, re.IGNORECASE)
# premium = 0
# for g1, g2 in result:
#     g1v = int(g1.replace(',',''))
#     if g1v > premium:
#         premium = g1v
    
# print(premium)
# print(outputString)
# pdfFile.close()


 
# from selenium import webdriver
# import time
# driver = webdriver.PhantomJS(executable_path= os.getcwd() + '\phantomjs.exe') #windows code
# driver.get("http://phx.corporate-ir.net/External.File?item=UGFyZW50SUQ9NTc5MzE0fENoaWxkSUQ9Mjg0MjM1fFR5cGU9MQ==&amp;t=1")
# time.sleep(3)
# print(driver.page_source)
# driver.close()
