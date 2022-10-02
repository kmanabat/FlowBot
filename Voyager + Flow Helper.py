from discord import embeds
from discord.ext import commands
import pandas as pd
import discord
import json
import os
import finviz
import nest_asyncio
import io
import aiohttp
import dataframe_image as dfi
from finviz.screener import Screener

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

chanID = 6563513546834 #Enter your channel ID here
owner = 4446843134533 #Endter your User ID here
bot = commands.Bot(command_prefix='$', case_insensitive=True)
bot.remove_command('help')
database = DbHandler('database.json')
settings_db = DbHandler('database.json')
settings = settings_db.open()

filtersMain = ['cap_midover','fa_epsyoy1_o20','fa_salesqoq_o20','ind_stocksonly','ipodate_prev3yrs','sh_avgvol_o500','sh_price_o15','ta_sma20_pa','ta_sma200_pa','ta_sma50_pa']
filtersSqueeze = ['fa_epsyoy1_o20', 'ind_stocksonly','sh_avgvol_o300','sh_float_u20','sh_price_o10','sh_short_o10','ta_changeopen_u','ta_sma20_pa','ta_sma200_pa','ta_sma50_pa']
filtersClam = ['cap_midover','fa_epsyoy1_o20','fa_salesqoq_o20','ind_stocksonly','ipodate_prev3yrs','sh_avgvol_o500','sh_price_o15','ta_sma20_pa','ta_sma200_pa','ta_sma50_pa']

@bot.event
async def on_ready():
    print('Bot is looking for new members entry.....')


@bot.command()
async def flow(ctx, ticker):
    context = database.open()
    if ticker.lower() in context.keys():
        with open('database.json','r') as f:
            data = json.loads(f.read())
        specData = pd.json_normalize(data, record_path = [ticker])
        del specData['flowid']
        del specData['ordertype']
        del specData['sector']
        specData = specData[["date","time","ticker","expiry","strike","cp","spot","details","premium","score","type"]]
        dfi.export(specData, "flow.png", fontsize=16,table_conversion="matplot")
        await ctx.send(file=discord.File('flow.png'))
  #      os.remove('flow.png')
    else:
       await ctx.send("No data available for this ticker at this moment")
@bot.command()
async def scan(ctx,*arg):
    nest_asyncio.apply()
    scanName = "Main Scan"
    if (not arg or arg[0] == "main"):
        stock_list = Screener(filters=filtersMain, order='ticker')
    else:
        if (arg[0] == "sqz" or arg[0] == "squeeze"):
            stock_list = Screener(filters=filtersSqueeze, order='ticker')
            scanName = "Short Squeeze Scan"
        else:
            if (arg[0] == "clam"):
                stock_list = Screener(filters=filtersClam, order='ticker')
                scanName = "Clam Scan"      
    slist = '```'
    slist2 ='```'
    count = 0
    for stock in stock_list:  
        if count <40 :
            slist += stock['Ticker']
            for i in range(0,4-len(stock['Ticker'])):
                slist += " "
            slist += '\t$' + stock['Price']  
            for i in range(0,6-len(stock['Price'])):
                slist += " "
            slist += '\t' + stock['Change'] +'\n' 
            count+=1
        else:
            slist2 += stock['Ticker']
            for i in range(0,4-len(stock['Ticker'])):
                slist2 += " "
            slist2 += '\t$' + stock['Price']  
            for i in range(0,6-len(stock['Price'])):
                slist2 += " "
            slist2 += '\t' + stock['Change'] +'\n' 
    slist+= '```'
    slist2+= '```'
    embed = discord.Embed(color = discord.Color.red())
    embed.add_field(name = scanName, value=slist)
    embed2 = discord.Embed(color = discord.Color.red())
    embed2.add_field(name = scanName, value=slist2)
    await ctx.send(embed=embed)
    if (count >= 40):
        await ctx.send(embed=embed2)
@bot.command()
async def sendSC(ctx, *arg):
    if (ctx.author.id == owner):
        chan1 = bot.get_channel(chanID)
        nest_asyncio.apply()
        scanName = "Main Scan"
    if (not arg or arg[0] == "main"):
        stock_list = Screener(filters=filtersMain, order='ticker')
    else:
        if (arg[0] == "sqz" or arg[0] == "squeeze"):
            stock_list = Screener(filters=filtersSqueeze, order='ticker')
            scanName = "Short Squeeze Scan"
        else:
            if (arg[0] == "clam"):
                stock_list = Screener(filters=filtersClam, order='ticker')
                scanName = "Clam Scan"      
    slist = '```'
    slist2 ='```'
    count = 0
    for stock in stock_list:  
        if count <40 :
            slist += stock['Ticker']
            for i in range(0,4-len(stock['Ticker'])):
                slist += " "
            slist += '\t$' + stock['Price']  
            for i in range(0,6-len(stock['Price'])):
                slist += " "
            slist += '\t' + stock['Change'] +'\n' 
            count+=1
        else:
            slist2 += stock['Ticker']
            for i in range(0,4-len(stock['Ticker'])):
                slist2 += " "
            slist2 += '\t$' + stock['Price']  
            for i in range(0,6-len(stock['Price'])):
                slist2 += " "
            slist2 += '\t' + stock['Change'] +'\n' 
    slist+= '```'
    slist2+= '```'
    embed = discord.Embed(color = discord.Color.red())
    embed.add_field(name = scanName, value=slist)
    embed2 = discord.Embed(color = discord.Color.red())
    embed2.add_field(name = scanName, value=slist2)
    await chan1.send(embed=embed)
    if (count >= 40):
        await chan1.send(embed=embed2)

@bot.command()
async def scanta(ctx, *arg):
    nest_asyncio.apply()
    if (not arg or arg[0] == "main"):
        stock_list = Screener(filters=filtersMain, order='ticker')
    else:
        if (arg[0] == "sqz" or arg[0] == "squeeze"):
            stock_list = Screener(filters=filtersSqueeze, order='ticker')
    for stock in stock_list:
        my_url = "https://charts2.finviz.com/chart.ashx?t="+stock['Ticker']+"&ty=c&ta=1"
        async with aiohttp.ClientSession() as session:
            async with session.get(my_url) as resp:
                if resp.status != 200:
                    return await ctx.send('Could not download file for ' + stock['Ticker'])
                data = io.BytesIO(await resp.read())
                await ctx.send(file=discord.File(data, 'stock.png'))

@bot.command()
async def help(ctx):
    await ctx.send("**Available Commands** \n -$scan (main,sqz) \n -$c1 (ticker) **[1 Min Chart]** \n -$c5 (ticker) **[5 Min Chart]** \n -$cd (ticker) **[Daily Chart]** \n -$cw (ticker) **[Weekly Chart]**")

@bot.command()
async def c1(ctx,arg):
    my_url = "https://widgets.tc2000.com/ChartImageHandler.ashx?service=TCTEMPLATEWIDGET&sym="+arg+"&TF=1MIN&w=554&h=284&bars=83&widgetID=39470&ID=4790593"
    async with aiohttp.ClientSession() as session:
        async with session.get(my_url) as resp:
            if resp.status != 200:
                return await ctx.send('Could not download file' + arg)
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, 'stock.png'))

@bot.command()
async def c5(ctx,arg):
    my_url = "https://widgets.tc2000.com/ChartImageHandler.ashx?service=TCTEMPLATEWIDGET&sym="+arg+"&TF=5MIN&w=554&h=284&bars=83&widgetID=39470&ID=4790593"
    async with aiohttp.ClientSession() as session:
        async with session.get(my_url) as resp:
            if resp.status != 200:
                return await ctx.send('Could not download file' + arg)
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, 'stock.png'))

@bot.command()
async def cd(ctx,arg):
    my_url = "https://charts2.finviz.com/chart.ashx?t="+arg+"&ty=c&ta=1"
    async with aiohttp.ClientSession() as session:
        async with session.get(my_url) as resp:
            if resp.status != 200:
                return await ctx.send('Could not download file' + arg)
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, 'stock.png'))

@bot.command()
async def cw(ctx,arg):
    my_url = "https://charts2.finviz.com/chart.ashx?t="+arg+"&ty=c&ta=0&p=w&s=l"
    async with aiohttp.ClientSession() as session:
        async with session.get(my_url) as resp:
            if resp.status != 200:
                return await ctx.send('Could not download file' + arg)
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, 'stock.png'))

@bot.event
async def on_message(message):
    chan1 = bot.get_channel(chanID)

    # FLOW  ****BE SURE TO REPLACE CHANNEL IDS
    #Where Flow Finder is sending embeds
    sourceFlow = 546434135433 #REPLACE
    sourceGold = 454343543543 #REPLACE
    sourceDark = 534348384354 #REPLACE
    sourceAlpha = 543463843541 #REPLACE
    sourceUnus = 876843513135 #REPLACE

    #Where you want to send embeds (Add more channels)
    flowChanID = 616846351354 #REPLACE 
    goldChanID = 354354689648 #REPLACE
    darkChanID = 445354384354 #REPLACE
    alphaChanID = 46468435468 #REPLACE
    unusCHanID = 543543854638 #REPLACE
    if (message.channel.id == sourceFlow): #flow1
        chanflow = bot.get_channel(flowChanID)
        await chanflow.send(embed=message.embeds[0])


    if (message.channel.id == sourceGold): #golden
        chanGold = bot.get_channel(goldChanID)
        await chanGold.send("New Golden Sweep @everyone",embed=message.embeds[0])
       

    if (message.channel.id == sourceDark): #darkpool
        chanDark = bot.get_channel(darkChanID)
        await chanDark.send(embed=message.embeds[0])

    if (message.channel.id == sourceAlpha): #alpha1
        chanAlpha = bot.get_channel(alphaChanID)
        await chan1.send("New AI Alert @everyone", embed=message.embeds[0])

    if (message.channel.id == sourceUnus): #unusual
        chanUnusual = bot.get_channel(unusCHanID)
        await chanUnusual.send(embed=message.embeds[0])


    


    await bot.process_commands(message)
bot.run('TOKEN HERE')
