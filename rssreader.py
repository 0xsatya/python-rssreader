from bs4 import BeautifulSoup
import requests
import time
from plyer import notification
from telegram_post import telegram_post
from datetime import datetime
from pytz import timezone

headers = {
            'User-Agent': 'your-user-agent-here'
        }
 
class ReadRss:
 
    def __init__(self, rss_url, headers):
 
        self.url = rss_url
        self.headers = headers
        # self.n = ToastNotifier()
        # self.icon = "https://icons.iconarchive.com/icons/papirus-team/papirus-apps/512/upwork-icon.png"
        self.icon = r"G:\Workspaces_Freelance\Workspaces_PersonalProjects\RssReader-Python\upwork.ico"
        # self.icon_red =  r"G:\Workspaces_Freelance\Workspaces_PersonalProjects\RssReader-Python\upwork_red2.ico"
        self.poolingTime = 20 #in seconds
        self.totalLoops = 500000 #total time to run the program = tatalLoops * secs
        self.totalFirstTimeNotifications = 3 #total notifications to show on startup of the program
        self.higlightKeywords = ['nft' , 'erc-20', 'erc20', 'erc 20', 'token']
        self.windowsNotificationTimeout = 10
        self.updated_articles_dict = {}

    def getISTfromUTC(self, utctime):
        format = "%a, %d %b %Y %H:%M:%S %z"  
        formatIst = "%a, %d %b %Y %H:%M:%S %Z"  
        # now_utc = datetime.now(timezone('UTC'))
        # print(now_utc.strftime(format))
        utc_time = datetime.strptime(utctime, format)
        ist_time = utc_time.astimezone(timezone('Asia/Kolkata'))
        # print(ist_time.strftime(formatIst))
        return ist_time.strftime(formatIst)

    def showWindowNotification(self, job_title, job_desc, job_link, job_pubdate):
        desc1 = job_desc
        desc = desc1[0: 230]+'...' if(len(desc1) > 230) else desc1
        
        # title = job_title.replace('https://www.upwork.com/jobs/', '')
        # title1 = title.split("_%7E")[0].replace('-', ' ')
        title1 = job_title
        title2 = title1[0: 60]+'...' if(len(title1) > 64) else title1
        desc = desc.replace('<br />', ' ')
        
        job_pubdate = self.getISTfromUTC(job_pubdate)
        notification.notify(title = title2, message= desc, app_icon = self.icon,timeout = self.windowsNotificationTimeout,toast = True)
        self.telegramPost(job_title = title1, job_desc = desc1, job_link = job_link,  job_pubdate = job_pubdate)

    def telegramPost(self, job_title, job_desc, job_link, job_pubdate):
        # print('---------POSTING IN TELEGRAM---------')
        try:
            job_desc = job_desc.replace('<br />', '\n')
            # print(job_desc)
            jt = 'Job title:\n⚡️ <b>'+job_title.replace('- Upwork', '')+'</b>'
            jd = '<b>Job Posted on:</b>\t'+job_pubdate + '\n\n<b>Job Description </b>\n\n'+job_desc+'\n'+job_link
            print('title:', jt)
            print('length of title:', len(jt))
            print('length of des:', len(jd))
            jd = jd[0: 4095]+'...' if(len(jd) > 4095) else jd
            telegram_post().postToChannel(job_title = jt, job_desc = jd)
        except ValueError:
            print("Error while posting to telegram:", ValueError)


    def getData(self):
        try:
            self.r = requests.get(self.url, headers=self.headers)
            self.status_code = self.r.status_code
        except Exception as e:
            print('Error fetching the URL: ', self.url)
            print(e)

        try:    
            self.soup = BeautifulSoup(self.r.text, 'xml')
        except Exception as e:
            print('Could not parse the xml: ', self.url)
            print(e)

        # print(self.soup.prettify())
        self.articles = self.soup.find_all('item')

        # self.articles_dicts = [{'title':a.find('title').text,'link':a.find('link').text,'description':a.find('description').text, 'pubdate':a.find('pubdate').text} for a in self.articles] 
        self.articles_dicts = []
        for a in self.articles:
            self.articles_dicts.append({'title': a.title.text, 'link': a.link.text, 'description': a.description.text, 'pubdate': a.pubDate.text})

        self.urls = [d['link'] for d in self.articles_dicts if 'link' in d]
        self.titles = [d['title'] for d in self.articles_dicts if 'title' in d]
        self.descriptions = [d['description'] for d in self.articles_dicts if 'description' in d]
        self.pub_dates = [d['pubdate'] for d in self.articles_dicts if 'pubdate' in d]
        
        self.final_dict = {}
        for item in self.articles_dicts:
            if 'pubdate' in item:
                self.final_dict[item['pubdate']] = item
        # print('Total jobs fetched:', len(self.final_dict))
        return self.final_dict

    def getNewArticles(self, oldDict, newDict):
        oldArticlesKeys = oldDict.keys()
        newArticlesKeys = newDict.keys()
        res = [i for i in newArticlesKeys if i not in oldArticlesKeys]
        temp_dict = {}
        for item in res:
            temp_dict[item] = newDict[item]
        # print('Total new articles::', len(temp_dict))
        return temp_dict

    def start(self):
        i = 0
        temp_dict = {}
        while i < self.totalLoops:
            new_articles = {}
            print('--------FETCHING--------')
            if i == 0:
                temp_dict = self.getData()
                self.updated_articles_dict = temp_dict
                # print('Started: Jobs fetched for first time :\n', self.updated_articles_dict)
                ti = 0
                jobItems = self.updated_articles_dict.items()
                for key, value in jobItems:
                    self.showWindowNotification(value['title'], value['description'], value['link'], value['pubdate'])         
                    ti += 1
                    if ti >= self.totalFirstTimeNotifications:
                        break
            else:
                temp_dict = self.getData()
                new_articles = self.getNewArticles(self.updated_articles_dict, temp_dict)
                # print(new_articles)
                # print('************************************')
                print('New jobs :\t', len(new_articles))
                
                if(len(new_articles) > 0):
                    ti = 0
                    jobItems = new_articles.items()
                    for key, value in jobItems:
                        self.showWindowNotification(value['title'], value['description'], value['link'], value['pubdate'])         
                print("Total Jobs :\t", len(self.updated_articles_dict))
                # print('************************************')
                self.updated_articles_dict.update(temp_dict)
            i +=1
            time.sleep(self.poolingTime)

if __name__ == '__main__':
    
    # Link for only Blockchain jobs
    feedLink = 'https://www.upwork.com/ab/feed/topics/rss?securityToken=7647847624562659cbc62f566570ba56e919864f3e95ef300fcc4421e0e7899751b470a0e99943933f6c5d71a9ce963fa7cf9bde6b2917bf8d3d491833d86c31&userUid=1226742287919726592&orgUid=1226742287936503809&topic=5158621'
    
    # Link for all upwork jobs
    feedLink1 = 'https://www.upwork.com/ab/feed/topics/rss?securityToken=7647847624562659cbc62f566570ba56e919864f3e95ef300fcc4421e0e7899751b470a0e99943933f6c5d71a9ce963fa7cf9bde6b2917bf8d3d491833d86c31&userUid=1226742287919726592&orgUid=1226742287936503809'
    
    feed = ReadRss(feedLink, headers)
    feed.start()

    