from lib.utility import *
from tornado.ioloop import IOLoop
import requests
from bs4 import BeautifulSoup
import math
import json

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
        self.m_header = ""
        self.m_exist_path = ""
        self.m_report_path = ""
        self.m_sync_time_s = 3 * 60 * 60

        self.Init()

    def Start(self):
        Log("Worker start method is called.")

        # todo: start
        self.RAKUYA()

        IOLoop.current().start()

    def Init(self):
        Log("Worker Worker init")

        # test
        self.m_id = 0
        self.m_rakuya_url = "https://www.rakuya.com.tw/sell/result?city=8&zipcode=404&price=~1200&size=22~&usecode=1&room=3~&floor=4~&age=~22&other=P&sort=11&browsed=0"
        self.m_rakuya_url = "https://www.rakuya.com.tw/sell/result?city=8&zipcode=406%2C404&price=~1200&size=22~&usecode=1&room=3~&floor=4~&age=~22&other=P&sort=11&browsed=0"
        # self.m_rakuya_url = "https://www.rakuya.com.tw/sell/result?city=8&zipcode=404&price=500~1000&size=20~30&sort=11&browsed=0"
        self.m_header = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
        self.m_exist_path = "report/exist.txt"
        self.m_report_path = "report/report"
        self.m_sync_time_s = 3 * 60 * 60 # 3 hours

    def RAKUYA(self):
        Log("RAKUYA GO")

        type = 0

        if self.m_rakuya_url is None or self.m_rakuya_url == "":
            Log("RAKUYA url is none")
            return

        url = self.m_rakuya_url
        headers = self.m_header

        # get url
        resp = requests.get(url, headers = headers)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # get pages cnt
        allcnt = int(soup.findAll("span", "numb setSearchTotal")[0].text.strip())
        pageitemcnt = 19
        pages = math.ceil(allcnt / pageitemcnt)

        # # test
        # pages = 1

        # get exist
        existList = self.GetExistData()

        # get all
        realdata = []
        for page in range(pages):
            time.sleep(0.1)

            # get item url
            pageurl = url + "&page=" + str(page + 1)
            resp = requests.get(pageurl, headers=headers)
            soup = BeautifulSoup(resp.text, 'html.parser')

            # get data
            allinfos = soup.findAll('section', class_='grid-item search-obj')
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

        # do send me
        self.End(realdata, self.m_id, type)

        # loop
        time.sleep(self.m_sync_time_s)
        self.RAKUYA()

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
                    # todo: write file
                    try:
                        f.write(str(data.work_id) + " " + str(data.type) + " " + str(data.uuid) + "\n")
                        rpf.write(data.uuid + "\n")
                        rpf.write(data.hef + "\n")
                        rpf.write(data.txt + "\n")
                        rpf.write(data.map + "\n")
                        rpf.write(data.data + "\n")
                        rpf.write(data.price + "\n")
                        rpf.write("-----------------------------------------------------" + "\n")

                        Log(data.uuid)
                        Log(data.hef)
                        Log(data.txt)
                        Log(data.map)
                        Log(data.data)
                        Log(data.price)
                        Log("-----------------------------------------------------")
                    except:
                        Log("Error")
                        Log(data)
                        Log("-----------------------------------------------------")
                f.close()
                rpf.close()
            else:
                Log("is none...")
            self.Notify(realdata)

    def Notify(self, realdata):
        vdata = "is non..."
        if len(realdata) > 0 :
            vdata = ""
            for data in realdata:
                # todo: write file
                try:
                    vdata = vdata + data.uuid + "\n"
                    vdata = vdata + data.hef + "\n"
                    vdata = vdata + data.txt + "\n"
                    vdata = vdata + data.map + "\n"
                    vdata = vdata + data.data + "\n"
                    vdata = vdata + data.price + "\n"
                    vdata = vdata + "-----------------------------------------------------" + "\n"
                except:
                    vdata = vdata + "Error"
                    vdata = vdata + "-----------------------------------------------------" + "\n"
        d = {
            "psw": "!@34001?>f!&&",
            "key": "broadcast",
            "value": vdata
        }
        print(d)
        requests.post('https://leori-houserobot2.herokuapp.com/action', data = json.dumps(d))
        # requests.post('http://192.168.1.103:5123/action', data = json.dumps(d))
