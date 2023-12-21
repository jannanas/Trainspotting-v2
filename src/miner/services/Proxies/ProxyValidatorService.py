import concurrent.futures
import requests
import csv
import os

class ProxyValidatorService:
    def __init__(self):
        self.path = fr"{os.getcwd()}\output\proxies_21_12_2023.csv"


    def validateProxy(self, proxy):
        proxies = {
            'http': proxy,
            'https': proxy
        }
        try:
            response = requests.get("https://pass.rzd.ru/tickets/public/en?layer_name=e3-route&st0=Sankt-Peterburg&code0=2004000&st1=Moscow&code1=2000000&dt0=13.03.2024&tfl=3&md=0&checkSeats=0", proxies=proxies, timeout=3) # httpbin.org/ip
            if (response.status_code == 200):
                print(proxy)
                return proxy
        except:
            pass


    def validateProxies(self):
        proxyList = []
        with open(self.path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                proxyList.append(row[0])                
        
        validProxies = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for result in executor.map(self.validateProxy, proxyList):
                if result != None:
                    validProxies.append(result)
        
        return validProxies


test = ProxyValidatorService()
validProxies = test.validateProxies()
print()

