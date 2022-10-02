import time, bs4, os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import traceback
from datetime import datetime
from discord_webhook import DiscordEmbed, DiscordWebhook
import json


class DbHandler:
    def __init__(self, file):
        self.file = file

    def dump(self, context):
        while True:
            try:
                with open(self.file, 'w') as w:
                    json.dump(context, w, indent=2)
                break
            except:
                pass

    def open(self):
        while True:
            try:
                with open(self.file) as r:
                    return json.load(r)
            except:
                pass

print(os.getcwd())

#MAKE database.json (empty) AND settings.json (FILL WITH WEBHOOKS URLS + USERNAME AND PASSWORD) 
database = DbHandler('database.json')
settings_db = DbHandler('settings.json')
settings = settings_db.open()
purple_url = settings['purple_url']
golden_url = settings['golden_url']
darkpool_url = settings['darkpool_url']
ai_url = settings['ai_url']
usual_url = settings['usual_url']


user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"
chromeOptions = webdriver.FirefoxOptions()
chromeOptions.add_argument("--start-maximized")
chromeOptions.headless = True
chromeOptions.add_argument(f'user-agent={user_agent}')
chromeOptions.add_argument("--window-size=1920,1080")
chromeOptions.add_argument('--ignore-certificate-errors')
chromeOptions.add_argument('--allow-running-insecure-content')
chromeOptions.add_argument("--disable-extensions")
chromeOptions.add_argument("--proxy-server='direct://'")
chromeOptions.add_argument("--proxy-bypass-list=*")
chromeOptions.add_argument('--disable-gpu')
chromeOptions.add_argument('--disable-dev-shm-usage')
chromeOptions.add_argument('--no-sandbox')
browser = webdriver.Firefox(options=chromeOptions, executable_path='geckodriver')
browser.maximize_window()
browser.implicitly_wait(20)
browser.get("https://app.flowalgo.com/")

time.sleep(10)
browser.find_element_by_xpath('//input[@name="amember_login"]').send_keys(settings['username'])

browser.find_element_by_xpath('//input[@name="amember_pass"]').send_keys(settings['password'])

browser.find_element_by_xpath('//*[@id="login"]/input[2]').send_keys(Keys.ENTER)
time.sleep(10)
try:
    browser.find_element_by_xpath('//*[@id="data-agreement-notice"]/button').click()
except:
    pass


print('started')


def flow_finder(datas):
    try:
        flows = datas.find_all(class_='data-body')[0]
        single_flow = flows.find_all(class_='item')
        response_list = []
        i = 0
        for each in single_flow:
            i += 1
            if i > 5:
                break
            golden = each.attrs['data-agsweep']
            purple = each.attrs['data-unusual']
            flow_id = each.attrs['data-flowid']
            order_type = each.attrs['data-ordertype']
            premium = each.attrs['data-premiumpaid']
            algo_score = each.attrs['data-score']
            sector = each.attrs['data-sector']
            ticker = each.attrs['data-ticker']
            sentiment = each.attrs['data-sentiment']
            time = each.find(class_='time').find('span').getText()
            expiry = each.find(class_='expiry').find('span').getText()
            spot = each.find(class_='ref').find('span').getText()
            strike = each.find(class_='strike').find('span').getText()
            details = each.find(class_='details').find('span').getText()
            response = dict()
            if 'true' in golden:
                response['type'] = 'gold'
            elif 'true' in purple:
                response['type'] = 'purple'
            else:
                response['type'] = 'general'
            if 'bull' in sentiment:
                response['cp'] = 'Calls'
            else:
                response['cp'] = 'Puts'
            response['flowid'] = int(flow_id.strip())
            response['ordertype'] = order_type.strip()
            response['premium'] = premium.strip()
            response['score'] = int(float(algo_score))
            response['sector'] = sector.strip()
            response['ticker'] = ticker.strip()
            response['time'] = time.strip()
            response['expiry'] = expiry.strip()
            response['spot'] = spot.strip()
            response['strike'] = strike.strip()
            response['details'] = details.strip()
            response['date'] = date = str(datetime.today().date())[2:]
            response_list.append(response)
        return response_list
    except:
        print(traceback.format_exc())
        return None


def darkpool_finder(datas):
    try:
        darkpool = datas.find_all(class_='data-body')[1]
        single_darkpool = darkpool.find_all(class_='item')
        response_list = []
        i = 0
        for each in single_darkpool:
            i += 1
            if i > 3:
                break
            flow_id = each.attrs['data-flowid']
            time = each.find(class_='time').find('span').getText()
            ticker = each.find(class_='ticker').find('span').getText()
            mm = each.find(class_='notional').find('span').getText()
            spot = each.find(class_='ref').find('span').getText()
            quantity = each.find(class_='quantity').find('span').getText()
            response = dict()
            response['flowid'] = int(flow_id.strip())
            response['time'] = time.strip()
            response['ticker'] = ticker.strip()
            response['mm'] = mm.strip()
            response['spot'] = spot.strip()
            response['quantity'] = quantity.strip()
            response_list.append(response)
        return response_list
    except:
        print(traceback.format_exc())
        return None


def ai_finder(datas):
    try:
        ai = datas.find(class_='alpha-ai-signals')
        single_ai = ai.find_all(class_='aai_signal')
        response_list = []
        i = 0
        for each in single_ai:
            i += 1
            if i > 2:
                break
            flow_id = each.attrs['data-flowid']
            date = each.find(class_='date').find('span').getText()
            ticker = each.find(class_='symbol').find('span').getText()
            #ref = each.find_all('span')[2].getText()
            ref = each.find_all(attrs={'style': 'font-size: 1.1rem'})[0].getText()
            sentiment = each.find(class_='sentiment').find('span').getText().strip()
            response = dict()
            response['flowid'] = int(flow_id.strip())
            response['date'] = date.strip()
            response['ticker'] = ticker.strip()
            response['ref'] = ref.strip()
            response['sentiment'] = sentiment.strip()
            response_list.append(response)
        return response_list
    except:
        print(traceback.format_exc())
        return None


def process(which, details):
    date = str(datetime.today().date())[2:]
    if which == 1:
        general = DiscordWebhook(url=usual_url)
        purple = DiscordWebhook(url=purple_url)
        golden = DiscordWebhook(url=golden_url)
        clr = 0x80ff80
        if details['cp'] == 'Puts':
            clr=0xff8080
        elif details['cp'] == 'Calls':
            clr=0x80ff80
        if details['type'] == 'gold':
            clr=0xffd700
        elif details['type'] == 'purple':
            clr=0x6a0dad
        embed = DiscordEmbed(title=f"{details['ticker'].upper()} {details['cp'].upper()}", color=clr)
        embed.add_embed_field(name='Date', value=date, inline=True)
        embed.add_embed_field(name='Time', value=details['time'], inline=True)
        embed.add_embed_field(name='Ticker', value=details['ticker'], inline=True)
        embed.add_embed_field(name='Exp', value=details['expiry'], inline=True)
        embed.add_embed_field(name='Strike', value=details['strike'], inline=True)
        embed.add_embed_field(name='C/P', value=details['cp'], inline=True)
        embed.add_embed_field(name='Spot', value=details['spot'], inline=True)
        embed.add_embed_field(name='Details', value=details['details'], inline=True)
        embed.add_embed_field(name='Type', value=details['ordertype'], inline=True)
        embed.add_embed_field(name='Prem', value=details['premium'], inline=True)
        embed.add_embed_field(name='Algo Score', value=details['score'], inline=True)
        embed.add_embed_field(name='Sect', value=details['sector'], inline=True)
        if details['type'] == 'gold':
            golden.add_embed(embed)
            golden.execute()
            return
        elif details['type'] == 'purple':
            purple.add_embed(embed)
            purple.execute()
            return
        else:
            general.add_embed(embed)
            general.execute()
            return
    elif which == 2:
        darkpool = DiscordWebhook(url=darkpool_url)
        embed = DiscordEmbed(title=f"{details['ticker'].upper()}", color=0x000000)
        embed.add_embed_field(name='Date', value=date, inline=True)
        embed.add_embed_field(name='Time', value=details['time'], inline=True)
        embed.add_embed_field(name='Ticker', value=details['ticker'], inline=True)
        embed.add_embed_field(name='Quantity', value=details['quantity'], inline=True)
        embed.add_embed_field(name='Spot', value=details['spot'], inline=True)
        embed.add_embed_field(name='$MM ', value=details['mm'], inline=True)
        darkpool.add_embed(embed)
        darkpool.execute()
        return
    else:
        ai = DiscordWebhook(url=ai_url)
        if 'short' in details['sentiment'].lower():
            embed = DiscordEmbed(title=f"{details['ticker'].upper()} AI Alert", color=0xff8080)
        elif 'long' in details['sentiment'].lower():
            embed = DiscordEmbed(title=f"{details['ticker'].upper()} AI Alert", color=0x80ff80)
        embed.add_embed_field(name='Symbol', value=details['ticker'], inline=True)
        embed.add_embed_field(name='Ref', value=details['ref'], inline=True)
        embed.add_embed_field(name='Signal', value=details['sentiment'], inline=True)
        ai.add_embed(embed)
        ai.execute()
        return


def data_process(datas):
    context = database.open()
    ticker = datas[0]['ticker'].lower()
    if ticker in context.keys():
        if len(context[ticker]) >= 20:
            context[ticker] = context[ticker][1:]
            context[ticker].append(datas[0])
        else:
            context[ticker].append(datas[0])
    else:
        context[ticker] = [datas[0]]
    database.dump(context)


saved_flow = None
saved_darkpool = None
saved_ai = None
while True:
    innerHTML = browser.execute_script("return document.body.innerHTML")
    parser_html = bs4.BeautifulSoup(innerHTML, "html.parser")
    flow_response = flow_finder(parser_html)
    darkpool_response = darkpool_finder(parser_html)
    ai_response = ai_finder(parser_html)
    if flow_response:
        touched = False
        if not saved_flow:
            data_process(flow_response)
            process(1, flow_response[0])
            saved_flow = flow_response[0]['flowid']

        elif saved_flow != flow_response[0]['flowid']:
            for each in flow_response:
                if each['flowid'] == saved_flow:
                    saved_flow = flow_response[0]['flowid']
                    touched = True
                    break
                data_process([each])
                process(1, each)
            if not touched:
                saved_flow = flow_response[0]['flowid']
    if darkpool_response:
        touched = False
        if not saved_darkpool:
            process(2, darkpool_response[0])
            saved_darkpool = darkpool_response[0]['flowid']
        elif saved_darkpool != darkpool_response[0]['flowid']:
            for each in darkpool_response:
                if each['flowid'] == saved_darkpool:
                    saved_darkpool = darkpool_response[0]['flowid']
                    touched = True
                    break
                process(2, each)
            if not touched:
                saved_darkpool = darkpool_response[0]['flowid']
    if ai_response:
        touched = False
        if not saved_ai:
            process(3, ai_response[0])
            saved_ai = ai_response[0]['flowid']
        elif saved_ai != ai_response[0]['flowid']:
            for each in ai_response:
                if each['flowid'] == saved_ai:
                    saved_ai = ai_response[0]['flowid']
                    touched = True
                    break
                process(3, each)
            if not touched:
                saved_ai = ai_response[0]['flowid']

