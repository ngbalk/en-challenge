from bs4 import BeautifulSoup
from urlparse import urljoin
import urllib2, re, json, time


class WebScraper():

    """Scrape company data"""
    rootUrl = None
    urlsVisited = {}
    urlQueue = []
    failed = []

    # properties
    timeoutVal = 15 # in seconds

    def __init__(self, url="http://data-interview.enigmalabs.org/companies/"):
        self.rootUrl = url

    def scrape(self):
        urlsVisited = {}
        failed = []
        allData = []

        # add initial set of urls to get started
        self.__parseAndAddUrls(self.rootUrl)

        while self.urlQueue:

            # space out request to avoid overloading server
            time.sleep(.1)

            # pop new url from queue
            urlToVisit = self.urlQueue.pop(0)

            print "visiting url: " + urlToVisit

            # discover new, univisited urls
            self.__parseAndAddUrls(urlToVisit)

            # if this is a company page, parse company data
            companyPageRegex = re.compile("companies/([A-Z]|[a-z])")
            if(companyPageRegex.search(urlToVisit)):
                companyData = self.__parseCompanyInformation(urlToVisit)

                # if succesfully parsed
                if companyData:
                    allData.append(companyData)

        # print json object
        self.__writeJson(allData,"solution.json")

        # print failed urls
        self.__writeJson(self.failed,"failed.json")


    def __parseAndAddUrls(self, url):

        print "dicovering new urls"

        # get soup for url
        soup = self.__getSoup(url)

        # failed to parse
        if not soup:
            return

        # get all links to other pages
        for tag in soup.find_all("a"):

            # join base to relative url
            urlToVisit = self.__joinRelativeUrl(tag['href'])

            # addToQueue
            if(urlToVisit not in self.urlsVisited):

                # mark that we have visited this url
                self.urlsVisited[urlToVisit] = 1

                # add to queue for scraping
                self.urlQueue.append(urlToVisit)


    def __parseCompanyInformation(self, url):

        print "parsing company data"

        companySoup = self.__getSoup(url)

        # if failed
        if not companySoup:
            return None

        company = {}

        # parse table into dictionary
        for row in companySoup.find_all('tr'):
            aux = row.findAll('td')
            company[aux[0].string] = aux[1].string

        return company


    def __joinRelativeUrl(self, relativeUrl):
        return "%20".join(urljoin(self.rootUrl,relativeUrl).split(" "))


    def __getSoup(self, url):
        try:
            doc = urllib2.urlopen(url, timeout=self.timeoutVal).read()
            soup = BeautifulSoup(doc, 'html.parser')
            return soup
        except:
            # if its our first failure on this url, add back to queue and try again
            if url not in self.failed:
                print "retrying on: " + url
                self.urlQueue.append(url)
            else:
                self.failed.append(url)
                print "failed on: " + url
            return None

    def __writeJson(self, data, fileName):
        with open(fileName, 'w') as outfile:
            json.dump(data, outfile)



webScraper = WebScraper("http://data-interview.enigmalabs.org/companies/")
webScraper.scrape()
