import sys
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import re, os, time
import urllib, urllib2
import json


#import librtmp

addon_handle = int(sys.argv[1])

#Localisation
local_string = xbmcaddon.Addon(id='plugin.video.livestream').getLocalizedString
ROOTDIR = xbmcaddon.Addon(id='plugin.video.livestream').getAddonInfo('path')
ICON = ROOTDIR+"/icon.png"
FANART = ROOTDIR+"/fanart.jpg"

    
def CATEGORIES():                    
    addDir('Live & Upcoming','/livestream',100,ICON,FANART)
    addDir('Search','/search',102,ICON,FANART)
     


def LIST_STREAMS():
        url = 'http://api.new.livestream.com/curated_events?page=1&maxItems=200'
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)                    
        json_source = json.load(response)
        response.close()

        for event in json_source['data']:            
            event_id = str(event['id'])
            owner_id = str(event['owner_account_id'])
            name = event['full_name'].encode('utf-8')
            icon = event['logo']['url']
            
            if event['in_progress']:
                name = '[COLOR=FF00B7EB]'+name+'[/COLOR]'

            addDir(name,'/live_now',101,icon,FANART,event_id,owner_id)

def SEARCH():
    '''
    POST http://7kjecl120u-2.algolia.io/1/indexes/*/queries HTTP/1.1
    Host: 7kjecl120u-2.algolia.io
    Connection: keep-alive
    Content-Length: 378
    X-Algolia-Application-Id: 7KJECL120U
    Origin: http://livestream.com
    X-Algolia-API-Key: 98f12273997c31eab6cfbfbe64f99d92
    User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36
    Content-type: application/json
    Accept: */*
    Referer: http://livestream.com/watch
    Accept-Encoding: gzip, deflate
    Accept-Language: en-US,en;q=0.8

    {"requests":[{"indexName":"events","params":"query=summ&hitsPerPage=3"},{"indexName":"accounts","params":"query=summ&hitsPerPage=3"},{"indexName":"videos","params":"query=summ&hitsPerPage=3"},{"indexName":"images","params":"query=summ&hitsPerPage=3"},{"indexName":"statuses","params":"query=summ&hitsPerPage=3"}],"apiKey":"98f12273997c31eab6cfbfbe64f99d92","appID":"7KJECL120U"}
    '''
    search_txt = ''
    dialog = xbmcgui.Dialog()
    search_txt = dialog.input('Enter search text', type=xbmcgui.INPUT_ALPHANUM)

    if search_txt != '':

        url = 'http://7kjecl120u-2.algolia.io/1/indexes/*/queries'
        req = urllib2.Request(url)
        req.addheaders = [ ("Accept", "*/*"),
                            ("Accept-Language", "en-US,en;q=0.8"),
                            ("Accept-Encoding", "gzip, deflate"),
                            ("X-Algolia-Application-Id", "7KJECL120U"),
                            ("X-Algolia-API-Key", "98f12273997c31eab6cfbfbe64f99d92"),
                            ("Content-type", "application/json"),
                            ("Connection", "keep-alive"),
                            ("Referer", "http://livestream.com/watch"),
                            ("User-Agent",'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36')]                
        
        
        json_search = '{"requests":[{"indexName":"events","params":"query='+search_txt+'&hitsPerPage=3"},{"indexName":"accounts","params":"query='+search_txt+'&hitsPerPage=3"},{"indexName":"videos","params":"query='+search_txt+'&hitsPerPage=3"},{"indexName":"images","params":"query='+search_txt+'&hitsPerPage=3"},{"indexName":"statuses","params":"query='+search_txt+'&hitsPerPage=3"}],"apiKey":"98f12273997c31eab6cfbfbe64f99d92","appID":"7KJECL120U"}'

        response = urllib2.urlopen(req,json_search)
        json_source = json.load(response)
        response.close()

        #print json_source

        for hits in json_source['results']: 
            for event in hits['hits']:
                try:
                    print event
                    event_id = str(event['id'])
                    owner_id = str(event['owner_account_id'])
                    name = event['full_name'].encode('utf-8')
                    #icon = event['logo']['thumbnail']['url']
                    icon = event['logo']['large']['url']
                    
                    #if event['in_progress']:
                    #name = '[COLOR=FF00B7EB]'+name+'[/COLOR]'

                    addDir(name,'/live_now',101,icon,FANART,event_id,owner_id)
                except:
                    pass

            


def GET_STREAM(owner_id,event_id):
    url = 'http://api.new.livestream.com/accounts/'+owner_id+'/events/'+event_id+'/viewing_info'
    try:
        req = urllib2.Request(url)       
        response = urllib2.urlopen(req)                    
        json_source = json.load(response)
        response.close()

        #print json_source

        m3u8_url = json_source['streamInfo']['m3u8_url']
        print "M3U8!!!" + m3u8_url
        req = urllib2.Request(m3u8_url)
        response = urllib2.urlopen(req)                    
        master = response.read()
        response.close()
        cookie =  urllib.quote(response.info().getheader('Set-Cookie'))

        print cookie
        print master

        line = re.compile("(.+?)\n").findall(master)  

        for temp_url in line:
            if '.m3u8' in temp_url:
                print temp_url
                print desc                                
                addLink(name +' ('+desc+')',temp_url+'|Cookie='+cookie, name +' ('+desc+')', FANART)
            else:
                desc = ''
                start = temp_url.find('RESOLUTION=')
                if start > 0:
                    start = start + len('RESOLUTION=')
                    end = temp_url.find(',',start)
                    desc = temp_url[start:end]
                else:
                    desc = "Audio"
    except:
        pass

    

def addLink(name,url,title,iconimage,fanart=None):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setProperty('fanart_image',FANART)
    liz.setProperty("IsPlayable", "true")
    liz.setInfo( type="Video", infoLabels={ "Title": title } )
    if fanart != None:
        liz.setProperty('fanart_image', fanart)
    else:
        liz.setProperty('fanart_image', FANART)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    return ok


def addDir(name,url,mode,iconimage,fanart=None,event_id=None,owner_id=None):       
    ok=True
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    if event_id != None:
        u = u+"&event_id="+urllib.quote_plus(event_id)
    if owner_id != None:
        u = u+"&owner_id="+urllib.quote_plus(owner_id)
    liz=xbmcgui.ListItem(name, iconImage=ICON, thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    if fanart != None:
        liz.setProperty('fanart_image', fanart)
    else:
        liz.setProperty('fanart_image', FANART)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)    
    return ok

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                    params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                    splitparams={}
                    splitparams=pairsofparams[i].split('=')
                    if (len(splitparams))==2:
                            param[splitparams[0]]=splitparams[1]
                            
    return param

params=get_params()
url=None
name=None
mode=None
event_id=None
owner_id=None

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass
try:
    event_id=urllib.unquote_plus(params["event_id"])
except:
    pass
try:
    owner_id=urllib.unquote_plus(params["owner_id"])
except:
    pass

print "Mode: "+str(mode)
#print "URL: "+str(url)
print "Name: "+str(name)
print "Event ID:"+str(event_id)
print "Owner ID:"+str(owner_id)



if mode==None or url==None or len(url)<1:
        #print ""                
        CATEGORIES()  

  
elif mode==100:
        #print "GET_YEAR MODE!"
        LIST_STREAMS()
elif mode==101:
        #print "GET_YEAR MODE!"
        GET_STREAM(owner_id,event_id)
elif mode==102:
        SEARCH()

xbmcplugin.endOfDirectory(addon_handle)
