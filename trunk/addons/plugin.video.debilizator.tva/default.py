# -*- coding: utf-8 -*-
#!/usr/bin/python
# Writer (c) 2012, Silhouette, E-mail: silhouette2022@gmail.com
# Rev. 0.7.4



import urllib,urllib2,re,sys,os,time
import xbmcplugin,xbmcgui,xbmcaddon

pluginhandle = int(sys.argv[1])
__addon__       = xbmcaddon.Addon(id='plugin.video.debilizator.tva') 
#fanart    = xbmc.translatePath( __addon__.getAddonInfo('path') + 'fanart.jpg')
#xbmcplugin.setPluginFanart(pluginhandle, fanart)

DTV_url = 'http://www.debilizator.tv'

dbg = 0

def dbg_log(line):
  if dbg: xbmc.log(line)

def getURL(url, data = None, cookie = None, save_cookie = False, referrer = None):
    #print url
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00')
    req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
    req.add_header('Accept-Language', 'ru,en;q=0.9')
    if cookie: req.add_header('Cookie', cookie)
    if referrer: req.add_header('Referer', referrer)
    if data: 
        response = urllib2.urlopen(req, data, timeout=30)
    else:
        response = urllib2.urlopen(req, timeout=30)
    link=response.read()
    if save_cookie:
        setcookie = response.info().get('Set-Cookie', None)
        #print "Set-Cookie: %s" % repr(setcookie)
        #print response.info()['set-cookie']
        if setcookie:
            try:
              setcookie = response.info()['set-cookie']
            except:
              pass
            link = link + '<cookie>' + setcookie + '</cookie>'
    
    response.close()
    #print response.info()
    return link

def DTV_start():
    
    dbg_log('-DTV_start')

    if 1:
        name='Live TV'
        item = xbmcgui.ListItem(name)
        uri = sys.argv[0] + '?mode=PRLS'
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
    
        name='Archives'
        item = xbmcgui.ListItem(name)
        uri = sys.argv[0] + '?mode=CHLS'
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
    
        xbmcplugin.endOfDirectory(pluginhandle)  
    else:
        DTV_online(DTV_url, 'CHLS')
        
        
def toLcTm(tzd, tmst):
    return time.strftime("%H:%M",time.localtime((time.mktime(tmst) - tzd*3600)))

def DTV_online(url, prls):
    dbg_log('-DTV_online')

    if prls == 'PRLS':
        dbg_log('FALSE:')
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')#movies episodes tvshows
        try:
            msktmht = getURL('http://time.jp-net.ru/');
            msktmls = re.compile('<h1 align=\'center\'>(.*?): (.*?)</h1>').findall(msktmht)
            msktmst = time.strptime(msktmls[0][1] + ' ' + msktmls[1][1], "%Y-%d-%m %H:%M:%S")
            tzdf = round( (time.mktime(msktmst) - time.mktime(time.localtime())) / (3600))
        except:
            pass

    try:
        http = getURL(url)
    except:
        xbmcplugin.endOfDirectory(pluginhandle)
        return
    oneline = re.sub( '\n', ' ', http)
    chndls = re.compile('div class="halfblock"> *?<a href="(.*?)/">(.*?)</div> *?</div> *?</div>').findall(oneline)
    #print chndls
    for chndel in chndls:
        #print chndel[1]
        chells = re.compile('<img class="chlogo" src="(.*?)" alt="(.*?)" title="(.*?)" />').findall(chndel[1])
        #print chells
        title = chells[0][2]
        if prls == 'PRLS':
            is_folder = False
        else:
            is_folder = True
        description = ''
        thumbnail = chells[0][0].replace('/mini', '')
        if prls == 'PRLS':
            uri = sys.argv[0] + '?mode=PLAY'
        else:
            uri = sys.argv[0] + '?mode=DTLS'
        uri += '&url='+urllib.quote_plus(url + '/' + chndel[0])
        uri += '&name='+urllib.quote_plus(title)
        #uri += '&plot='+urllib.quote_plus(description)
        uri += '&thumbnail='+urllib.quote_plus(thumbnail)
        ptlsln = 1
        ptls = re.compile('<div class="prtime">(.*?)</div> *?<div class="prdesc" title=".*?">(.*?)</div>').findall(chndel[1])
        #print ptls
        ptlsln = len(ptls)
        if prls == 'PRLS':
            i = 1
            while ptlsln - i + 1:
                prtm = ptls[ptlsln - i][0]
                prds = ptls[ptlsln - i][1]
                #prxt = ptls[ptlsln - i][2]
                prxt = ''

                prtmst = time.strptime(msktmls[0][1] + ' ' + prtm, "%Y-%d-%m %H:%M")
                
                try:
                    nprtm = toLcTm(tzdf, prtmst)
                except:
                    nprtm = prtm
                i += 1
                description = "[B][COLOR FF0084FF]" + nprtm + "[/COLOR] [COLOR FFFFFFFF]" + prds + "[/COLOR][/B][COLOR FF999999]" + chr(10) + prxt + "[/COLOR]" + chr(10) + description
                    
                
#                try:
#                    tmdf = time.mktime(msktmst) - time.mktime(prtmst)
#                    if (((tmdf < 0) and (tmdf > -12*3600.0)) or (tmdf > 12*3600.0)) and (ptlsln > 1):
#                        i += 1
#                    else:
#                        if i > 1:
#                            prtmst2 = time.strptime(msktmls[0][1] + ' ' + ptls[ptlsln - i + 1][0], "%Y-%d-%m %H:%M")
#                            prtm = toLcTm(tzdf, prtmst) + '-' + toLcTm(tzdf, prtmst2)
#                        else:
#                            prtm = toLcTm(tzdf, prtmst)
#                        title = prtm + " " + re.sub( '&quot;','\"',re.sub( '\(\.\.\.\)', '', prds))
#                        
#                        break
#                except:
#                    break
                    
                

        description = re.sub( '&quot;','\"',re.sub( '\(\.\.\.\)', '', description))
        if ptlsln:
            dbg_log(title)
            item=xbmcgui.ListItem(title, iconImage=thumbnail, thumbnailImage=thumbnail)
            item.setInfo( type='video', infoLabels={'title': title, 'plot': description})
            if prls == 'PRLS':
                item.setProperty('IsPlayable', 'true')
            #item.setProperty('fanart_image',thumbnail)
            xbmcplugin.addDirectoryItem(pluginhandle,uri,item,is_folder)
            dbg_log(uri)
    xbmcplugin.endOfDirectory(pluginhandle)

def DTV_play(url, name, thumbnail):
    dbg_log('-DTV_play')
    
    response    = getURL(url, save_cookie = True, referrer = DTV_url)
    mycookie = re.search('<cookie>(.+?)</cookie>', response).group(1)
    oneline = re.sub( '[\n\r\t]', ' ', response)
#    server_ls   = re.compile('<a href="/server/live/(.*?)"><div id="bar[0-9]" style="(.*?)"></div></a> *?<script type="text/javascript"> *?\$\(function\(\) \{ *?var val = (.*?);').findall(oneline)
#    if(len(server_ls)):
#        min = 999
#        new_srv = ""
#        for ssHref, ssCrap, ssVal in server_ls:
#            if(int(ssVal) < min):
#                min = int(ssVal)
#                new_srv = "/server/live/" + ssHref
                
#        if(new_srv != ""):
#            dbg_log('-NEW_SRV:'+ new_srv + '\n')
    new_srv = "/server/live/100500"
    response = getURL(DTV_url + new_srv, save_cookie = True, cookie = mycookie, referrer = url)
    mycookie = re.search('<cookie>(.+?)</cookie>', response).group(1)
                   
    response = getURL(DTV_url + '/maclist/', cookie = mycookie, referrer = url)
    streamer_ls   = re.compile('mvideo.src="(.*?)";').findall(response)
    
#    streamer_ls   = re.compile('<jwplayer:streamer>(.*?)</jwplayer:streamer>').findall(response)
#    file_ls   = re.compile('<enclosure url="(.*?)"').findall(response)
    
#    if len(streamer_ls):
#      if len(file_ls) :
#        rtmp_streamer = streamer_ls[0]
#        rtmp_file = file_ls[0]
#        SWFObject = DTV_url + '/player/' 
   
#        furl  = ''
#        furl += '%s/%s'%(rtmp_streamer,rtmp_file)
#        furl += ' swfUrl=%s'%SWFObject
#        furl += ' pageUrl=%s'%url
#        furl += ' tcUrl=%s'%rtmp_streamer
#        furl += ' swfVfy=True Live=True'

    if len(streamer_ls):
        furl = streamer_ls[0]
        xbmc.log('furl = %s'%furl)
        item = xbmcgui.ListItem(path = furl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)


def DTV_dates(url, thumbnail):
    dbg_log('-DTV_dates')

    item = xbmcgui.ListItem('Today', iconImage=thumbnail, thumbnailImage=thumbnail)
    uri = sys.argv[0] + '?mode=ARLS'
    uri += '&url='+urllib.quote_plus(url)
    uri += '&thumbnail='+urllib.quote_plus(thumbnail)
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
            
    http = getURL(url, save_cookie = True, referrer = DTV_url)
    mycookie = re.search('<cookie>(.+?)</cookie>', http).group(1)
    
    dtls = re.compile('<td style="(.*?)"><a rel="nofollow" href="(.*?)">(.*?)</a></td>').findall(http)
    if len(dtls):
        for style, href, descr in dtls:
            item = xbmcgui.ListItem(descr, iconImage=thumbnail, thumbnailImage=thumbnail)
            uri = sys.argv[0] + '?mode=ARLS'
            uri += '&url='+urllib.quote_plus(DTV_url + href)
            uri += '&name='+urllib.quote_plus(url)
            uri += '&thumbnail='+urllib.quote_plus(thumbnail)
            uri += '&cook='+urllib.quote_plus(mycookie)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  

    xbmcplugin.endOfDirectory(pluginhandle)
    
    

def DTV_archs(url, name2, thumbnail, mycook):
    dbg_log('DTV_archs')
    http = getURL(url, save_cookie = True, cookie = mycook, referrer = url)
    mycookie = re.search('<cookie>(.+?)</cookie>', http).group(1)
    
    oneline = re.sub( '\n', ' ', http)
    #dtls = re.compile('</(script|a)> *?<a title="(.*?)" href="(.*?)"> *?<div class="prtime">(.*?)</div> *?<div class="prdescfull" title="(.*?)">(.*?)</div> *?<div class="fulldivider"></div>').findall(oneline)
    dtls = re.compile('<a title="(.*?)" href="(.*?)"> *?<div class="prtime">(.*?)</div> *?<div class="prdescfull" title="(.*?)">(.*?)</div> *?</a>').findall(oneline)
    if len(dtls):
        for crap1, src, tm, plot, descr in dtls:
            name=tm + ' ' + descr.replace('&quot;', '\"')
            item = xbmcgui.ListItem(name, iconImage=thumbnail, thumbnailImage=thumbnail)
            uri = sys.argv[0] + '?mode=PLAR'
            uri += '&url='+urllib.quote_plus(DTV_url + src)
            uri += '&name='+urllib.quote_plus(name2)
            uri += '&cook='+urllib.quote_plus(mycookie)
            item.setInfo( type='video', infoLabels={'title': name, 'plot': plot})
            item.setProperty('IsPlayable', 'true')
            #item.setProperty('fanart_image',thumbnail)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item)
            dbg_log('uri:' + uri + '\n')  


    xbmcplugin.endOfDirectory(pluginhandle)    
    
def DTV_plarch(url, name, mycook):
    
    response = getURL(url, save_cookie = True, cookie = mycook)
    mycookie = re.search('<cookie>(.+?)</cookie>', response).group(1)
    
#    oneline = re.sub( '[\n\r\t]', ' ', response)
#    server_ls   = re.compile('<a href="/server/vod/(.*?)"><div id="bar[0-9]" style="(.*?)"></div></a> *?<script type="text/javascript"> *?\$\(function\(\) \{ *?var val = (.*?);').findall(oneline)
#    if(len(server_ls)):
#        min = 999
#        new_srv = ""
#        for ssHref, ssCrap, ssVal in server_ls:
#            if(int(ssVal) < min):
#                min = int(ssVal)
#                new_srv = "/server/vod/" + ssHref
                
#        if(new_srv != ""):
#            dbg_log('-NEW_SRV:'+ new_srv + '\n')
    new_srv = "/server/live/100500"
    response = getURL(DTV_url + new_srv, save_cookie = True, cookie = mycookie, referrer = url)
    mycookie = re.search('<cookie>(.+?)</cookie>', response).group(1)
            
    response = getURL(DTV_url + '/maclist/', cookie = mycookie, referrer = url)
    file_ls   = re.compile('mvideo.src="(.*?)";').findall(response)
    
    if len(file_ls):
        furl = file_ls[0]
        xbmc.log('furl = %s'%furl)
        item = xbmcgui.ListItem(path = furl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)
    
                   
#    response = getURL(DTV_url + '/playlist/', cookie = mycookie, referrer = url)
            
#    file_ls   = re.compile('<enclosure url="(.*?)"').findall(response)
    
#    sPlayList   = xbmc.PlayList(xbmc.PLAYLIST_VIDEO) 
#    sPlayer     = xbmc.Player()
#    sPlayList.clear()

#    if len(file_ls) :
#      i = 0
      
#      url2 = urllib.quote_plus(url)
#      dbg_log('url2 = %s'%url2)
#      name2 = urllib.quote_plus(name)
#      dbg_log('name2 = %s'%name2)
#      url2 = re.sub(name2, ' ', url2) 
#      dbg_log('url2 = %s'%url2)
#      url2 = re.sub('/', ' ', urllib.unquote_plus(url2) )
#      dbg_log('url3 = %s'%url2) 
      
#      try:
#        prtime = time.strptime(url2, " %Y-%m-%d %H:%M ")
#        stime = str(time.mktime(prtime) % 3600)
#        dbg_log('stime = %s'%stime)
#      except:
#        stime = '0.0'
	        
#      for furl in file_ls:
#        if i == 0:
#          item0 = xbmcgui.ListItem(path = furl)
#          xbmcplugin.setResolvedUrl(pluginhandle, True, item0)
#          dbg_log('furl0 = %s'%furl)
#          furl += '?start=' + stime

#        item = xbmcgui.ListItem(path = furl)
#        sPlayList.add(furl, item, i)
        
#        dbg_log('furl = %s'%furl)
#        i = i + 1

#    sPlayer.play(sPlayList)      


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
name=''
plot=''
mode=None
#thumbnail=fanart
thumbnail=''
cook=''

dbg_log('OPEN:')

try:
    mode=params['mode']
    dbg_log('-MODE:'+ mode + '\n')
except: pass
try:
    url=urllib.unquote_plus(params['url'])
    dbg_log('-URL:'+ url + '\n')
except: pass
try:
    name=urllib.unquote_plus(params['name'])
    dbg_log('-NAME:'+ name + '\n')
except: pass
try: 
    thumbnail=urllib.unquote_plus(params['thumbnail'])
    dbg_log('-THAMB:'+ thumbnail + '\n')
except: pass
try: 
    plot=urllib.unquote_plus(params['plot'])
    dbg_log('-PLOT:'+ plot + '\n')
except: pass
try: 
    cook=urllib.unquote_plus(params['cook'])
    dbg_log('-COOK:'+ cook + '\n')
except: pass




if mode == 'PLAY': DTV_play(url, name, thumbnail)
elif mode == 'PLAR': DTV_plarch(url, name, cook)
elif mode == 'PRLS': DTV_online(DTV_url, mode)
elif mode == 'CHLS': DTV_online(DTV_url, mode)
elif mode == 'DTLS': DTV_dates(url, thumbnail)
elif mode == 'ARLS': DTV_archs(url, name, thumbnail, cook)
elif mode == None: DTV_start()

dbg_log('CLOSE:')

