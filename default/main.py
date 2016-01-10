'''
Created on 2016/1/7

@author: K.Yao
'''

from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup


class Website():
    def __init__(self, url):
        self.__url = url # save root url
        self.__soup = self.__getSoup()
    

    def __getSoup(self, relativeurl = ''):
        try:
            conn = urlopen(self.__url + relativeurl)
        except HTTPError as e:
            print(e)
            return None
        try:
            soup = BeautifulSoup(conn.read())
        except AttributeError as e:
            print(e)
            return None
        return soup
    
    def getTitle(self):
        try:
            title = self.__soup.title.get_text()
        except AttributeError:
            return None
        return title


url = 'http://www.acelimited.com/'
site = Website(url)
print(site.getTitle().strip())
