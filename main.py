# import requests
# import asyncio

from src.tracker import TrackerServer


# async def test():
#     url = "https://www.rakuya.com.tw/search/sell_search/get-result?city=8&zipcode=404&price=500~1000&size=22~&usecode=1&typecode=R2&age=~22&sort=11&browsed=0&searchGroupId=6136c23964e30"
#     headers = ('User-Agent', 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Mobile Safari/537.36')
#     loop = asyncio.get_event_loop()
#     res = await loop.run_in_executor(None, requests.get, url, headers)
#     print(res.status_code)
#     print(res.text)

if __name__ == '__main__':

    TrackerServer().Start()

    # asyncio.get_event_loop().run_until_complete(test())