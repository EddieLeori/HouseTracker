from urllib import response
from lib.utility import *
from tornado.ioloop import IOLoop
import requests
from bs4 import BeautifulSoup
import math
import json
import random
import threading
import re
from fake_useragent import UserAgent

class HData:
    def __init__(self):
        self.work_id = ""
        self.type = ""
        self.uuid = ""
        self.hef = ""
        self.txt = ""
        self.map = ""
        self.data = ""
        self.price = ""


class Worker:
    def __init__(self):
        self.m_id = 0
        self.m_url = ""
        self.m_exist_path = ""
        self.m_report_path = ""
        self.m_sync_time_s = 3 * 60 * 60
        self.m_thread = None

        self.Init()

    def Start(self):
        Log("Worker start method is called.")

        # todo: start
        if self.m_thread is None:
            Log("thread error!")
            return
        
        self.m_thread.start()
        IOLoop.current().start()

    def Init(self):
        Log("Worker Worker init")

        # test
        self.m_id = 0
        # self.m_rakuya_url = "https://www.rakuya.com.tw/sell/result?city=8&zipcode=404&price=~1200&size=22~&usecode=1&room=3~&floor=4~&age=~22&other=P&sort=11&browsed=0"
        # self.m_rakuya_url = "https://www.rakuya.com.tw/sell/result?city=8&zipcode=406%2C404&price=~1200&size=22~&usecode=1&room=3~&floor=4~&age=~22&other=P&sort=11&browsed=0"
        self.m_rakuya_url = "https://www.rakuya.com.tw/sell/result?city=8&zipcode=406%2C404&price=~1200&size=22~&usecode=1&room=3~&other=P&sort=21&browsed=0"
                
        self.m_ips = ["127.0.0.1"]

        self.m_exist_path = "report/exist.txt"
        self.m_report_path = "report/report"
        self.m_sync_time_s = 3 * 60 * 60 # 3 hours

        # threading
        self.m_thread = threading.Thread(target=self.schedulePro)

    def schedulePro(self):
        while 1:
            self.RAKUYA()
            time.sleep(self.m_sync_time_s)
    
    def getHeaders(self):
        ua = UserAgent()
        user_agent = {"User-Agent": ua.random}
        return user_agent
    
    def updateIP(self):
        initip = "127.0.0.1"
        response = requests.get("https://www.sslproxies.org/")
        proxy_ips = re.findall('\d+\.\d+\.\d+\.\d+:\d+', response.text) #「\d+」代表數字一個位數以上
        self.m_ips = []
        for index, ip in enumerate(proxy_ips):
            try:
                if index <= 30:  #驗證30組IP
                    result = requests.get('https://ip.seeip.org/jsonip?',
                                        proxies={'http': ip, 'https': ip},
                                        timeout=5)
                    # print(result.json())
                    self.m_ips.append(ip)
            except:
                msf=f"{ip} invalid"
                # print(f"{ip} invalid")
        if self.m_ips is []:
            self.m_ips.append(initip)
        Log("update ip's count=" + str(len(self.m_ips)))

    def getIP(self):
        return random.choice(self.m_ips)
        
    def RAKUYA(self):
        Log("RAKUYA GO")

        type = 0
        realdata = []
        try:
            if self.m_rakuya_url is None or self.m_rakuya_url == "":
                Log("RAKUYA url is none")
                return

            url = self.m_rakuya_url
            self.updateIP()

            # get url
            Log("url="+url)
            ip = self.getIP()
            resp = requests.get(url, headers = self.getHeaders(), proxies={"http": "http://" + ip})
            if resp.status_code != 200:
                Log("resp status=" + str(resp.status_code) + " reason=" + str(resp.reason))
                return
            soup = BeautifulSoup(resp.text, 'html.parser')

            # get pages cnt
            pageitemcnt = 19
            soupdata = soup.find_all("span", class_="numb setSearchTotal")
            Log("count_total=" + str(len(soupdata)))
            if len(soupdata) > 0 :
                allcnt = int(soupdata[0].text.strip())
                pages = math.ceil(allcnt / pageitemcnt)

                # get exist
                existList = self.GetExistData()

                # get all
                for page in range(pages):
                    time.sleep(0.5)
                    try: 
                        # get item url
                        pageurl = url + "&page=" + str(page + 1)
                        ip = self.getIP()
                        resp = requests.get(pageurl, headers = self.getHeaders(), proxies={"http": "http://" + ip})
                        soup = BeautifulSoup(resp.text, 'html.parser')

                        # get data
                        allinfos = soup.find_all("section", class_="grid-item search-obj")
                        for item in allinfos:
                            data = HData()
                            data.work_id = self.m_id
                            data.type = type
                            data.uuid = item.attrs.get('data-ehid')
                            data.hef = item.find('a', class_ = 'browseItemDetail').get('href')
                            data.txt = item.find('div', class_='h2 title-2').text.strip()
                            data.map = item.find('h2', class_='address').text.strip()
                            data.data = item.find('ul', class_='list__info').text.strip()
                            data.price = item.find('div', class_='group__price').text.strip()

                            # check real
                            if self.CheckExist(existList, self.m_id, type, data.uuid) is False:
                                realdata.append(data)
                    except Exception as e:
                        Log("RAKUYA item except error!:" + str(e))
        except Exception as e:
            Log("RAKUYA except error!:" + str(e))
            return

        # end
        self.End(realdata, self.m_id, type)

    def GetExistData(self):
        content_list = []
        file = self.m_exist_path
        try:
            with open(file, 'r') as f:
                content_list = f.read().splitlines()
                f.close()
        except:
            Log(file + " is not exist")
        return content_list


    def CheckExist(self, content_list, workid, type, uuid):
        string = str(workid) + " " + str(type) + " " + str(uuid)
        if string in content_list:
                return True
        return False

    def End(self, realdata, work_id, type):
        if realdata is not None:
            if len(realdata) > 0:
                file = self.m_exist_path
                rpfile = self.m_report_path + "-" + str(work_id) + "-" + str(type) + "-" + CurrentDate() + ".txt"
                f = open(file, 'a')
                rpf = open(rpfile, 'a')
                for data in realdata:
                    try:
                        tmpdata = data.uuid + "\n" + data.hef + "\n" + data.txt + "\n" + data.map + "\n" + data.data + "\n" + data.price + "\n"
                        tmpdata = tmpdata + "-----------------------------------------------------" + "\n"
                        # send notiry and write file
                        if self.Notify(tmpdata) is True:    
                            f.write(str(data.work_id) + " " + str(data.type) + " " + str(data.uuid) + "\n")
                            rpf.write(tmpdata)
                    except Exception as e:
                        Log("End Error:" + str(e))
                        Log(data)
                        Log("-----------------------------------------------------")
                f.close()
                rpf.close()
            else:
                Log("is none...")
                self.Notify("is none...")

    def Notify(self, data):
        # Log(data)                        
        d = {
                "psw": "!@34001?>f!&&",
                "key": "notifyAll",
                "value": data
            }
        print(d)
        try:
            response = requests.post('http://127.0.0.1:5124/action', data = json.dumps(d))
            # response = requests.post('http://104.199.211.77:5124/action', data = json.dumps(d))
            # response = requests.post('http://192.168.1.103:5123/action', data = json.dumps(d))
            if response.status_code != 200:
                Log(response)
                return False
            return True
        except Exception as e:
            Log("notify server error:" + str(e))
            return False
        
        

