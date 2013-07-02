import urllib,urllib2,re,xbmc,xbmcplugin,xbmcaddon,xbmcgui,os,sys,commands,HTMLParser

website = 'http://www.990.ro/';

__version__ = "1.0.0"
__plugin__ = "990.ro" + __version__
__url__ = "www.xbmc.com"
settings = xbmcaddon.Addon( id = 'plugin.video.990ro' )

search_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'search.png' )
movies_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'movies.png' )
movies_hd_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'movies-hd.png' )
tv_series_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'tv.png' )
next_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'next.png' )

def ROOT():
    addDir('Filme','http://www.990.ro/toate-filmele-pagina-1.html',1,movies_thumb)
    addDir('Filme actualizate','http://www.990.ro/',2,movies_hd_thumb)
    addDir('Seriale','http://www.990.ro/',5,tv_series_thumb)
    addDir('Cauta filme','http://www.990.ro/',3,search_thumb)
    xbmc.executebuiltin("Container.SetViewMode(500)")

def FILME(url):
    link=get_url(url)
    match=re.compile('<a href="(filme-[0-9]+-.+?.html )" class=\'thumb\'><img src="(filme/.+?)" alt="(.+?)"', re.IGNORECASE).findall(link)
    for legatura, thumbnail, name in match:
        the_link = 'http://www.990.ro/'+legatura
        image = 'http://www.990.ro/'+thumbnail
        addDir(name,the_link,4,image)
    # pagina urmatoare
    match=re.compile('toate-filmele-pagina-([0-9]+).html', re.IGNORECASE).findall(url)
    nr_pagina = match[0]
    addNext('Next','http://www.990.ro/toate-filmele-pagina-'+str(int(nr_pagina)+1)+'.html', 1, next_thumb)
    xbmc.executebuiltin("Container.SetViewMode(500)")

def FILME_CALITATE_BUNA(url):
    link=get_url(url)
    match = re.compile('<a href="(filme-[0-9]+-.+?.html)" title=".+?">(.+?)</a><br />', re.IGNORECASE).findall(link)
    for legatura, name in match:
        #the_link = urllib.quote(url+legatura)
        the_link = url+legatura
        addDir(name,the_link,4,'')
        print 'legatura: '+url+legatura
    xbmc.executebuiltin("Container.SetViewMode(500)")

def CAUTA(url):
    print 'Cauta'
    keyboard = xbmc.Keyboard( '' )
    keyboard.doModal()
    if ( keyboard.isConfirmed() == False ):
        return
    search_string = keyboard.getText().replace( ' ', '+' )
    if len( search_string ) == 0:
        return
    
    page = 'http://www.990.ro/cauta2.php?text='+search_string+'&submit=Cauta'
    link = get_url(page)

    match=re.compile('<a href="(filme-[0-9]+-.+?.html )" class=\'thumb\'><img src="(filme/.+?)" alt="(.+?)"', re.IGNORECASE).findall(link)
    if len(match) > 0:
        for legatura, thumbnail, name in match:
            the_link = 'http://www.990.ro/'+legatura
            image = 'http://www.990.ro/'+thumbnail
            addDir(name,the_link,4,image)
    xbmc.executebuiltin("Container.SetViewMode(500)")
    

def SERIALE(url):
    link=get_url(url)
    match=re.compile('<li><a href="(seriale-[0-9]+-.+?.html)" title=".+?">(.+?)</a></li>', re.IGNORECASE).findall(link)
    for legatura,name in match:
        the_link = url+legatura
        addDir(name,the_link,6,'')

def SEZON(url):
    link=get_url(url)
    match=re.compile("><img src='img/sez([0-9]+).gif' alt='(.+?)'></", re.IGNORECASE).findall(link)
    for nr, sezon in match:
        addDir(sezon,url+'?sezon='+nr,7,'')

def EPISOADE(url):
    link=get_url(url)
    match=re.compile("sezon=([0-9]+)", re.IGNORECASE).findall(url)
    sezon = '0'+match[0] if int(match[0]) < 10 else match[0]  
    match=re.compile("Sezonul "+sezon+", (Episodul .+?)</div></td><td><a href='(seriale2-[0-9]+-[0-9]+-.+?.html)'>(.+?)</a>", re.IGNORECASE).findall(link)
    for nr, legatura, titlu in match:
        addDir(nr+' - '+titlu,'http://www.990.ro/'+legatura,8,'')

def VIDEO_EPISOD(url):
    match=re.compile("seriale2-([0-9]+-[0-9]+)-(.+?)-download", re.IGNORECASE).findall(url)
    id_episod = match[0][0]
    nume = match[0][1]
    legatura = 'http://www.990.ro/player-serial-'+id_episod+'-'+nume+'--sfast.html'
    link = get_url(legatura)
    match = re.compile('<center><center><a href=\'(.+?)\'><img src=\'.+?\'></a></center></center>', re.IGNORECASE).findall(link)
    fu_link = match[0]
    fu_source = get_url(fu_link)
    # fastupload flv url
    match=re.compile("'file': '(.+?).flv',", re.IGNORECASE).findall(fu_source)
    url_flv = match[0] + '.flv'
    # link catre video
    addLink('Redare video', url_flv+'?.flv','')

def VIDEO(url, name):
    #print 'url video '+url
    #print 'nume video '+name
    # thumbnail
    src = get_url(urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]"))
    match = re.compile('<h5></h5>\n.+?<img src=\'(.+?)\' alt=\'.+?\' /></td>', re.IGNORECASE).findall(src)
    thumbnail = 'http://www.990.ro/'+match[0]
    # calitate film
    match=re.compile('<td>Calitatea filmului: nota <b><u>(.+?)</u></b>', re.IGNORECASE).findall(src)
    calitate_film = match[0]
    #link trailer
    try:
        match=re.compile("'file': '(.+?)',", re.IGNORECASE).findall(src)
        link_youtube = match[0]
        link_video_trailer = youtube_video_link(link_youtube)
    except:
        link_video_trailer = ''
    # video id
    match=re.compile('990.ro/filme-([0-9]+)-.+?.html', re.IGNORECASE).findall(url)
    video_id = match[0]
    source_link = 'http://www.990.ro/player-film-'+video_id+'-sfast.html'
    link = get_url(source_link)
    match = re.compile('<center><center><a href=\'(.+?)\'><img src=\'.+?\'></a></center></center>', re.IGNORECASE).findall(link)
    fu_link = match[0]
    fu_source = get_url(fu_link)
    # fastupload flv url
    match=re.compile("'file': '(.+?).flv',", re.IGNORECASE).findall(fu_source)
    url_flv = match[0] + '.flv'
    # link catre video
    addLink('Redare video (calitatea filmului: nota '+calitate_film+')', url_flv+'?.flv',thumbnail)
    if link_video_trailer != '':
        addLink('Trailer film', link_video_trailer+'?.mp4', thumbnail)
    

def get_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link

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

def yt_get_all_url_maps_name(url):
    conn = urllib2.urlopen(url)
    encoding = conn.headers.getparam('charset')
    content = conn.read().decode(encoding)
    s = re.findall(r'"url_encoded_fmt_stream_map": "([^"]+)"', content)
    if s:
        s = s[0].split(',')
        s = [a.replace('\\u0026', '&') for a in s]
        s = [urllib2.parse_keqv_list(a.split('&')) for a in s]

    n = re.findall(r'<title>(.+) - YouTube</title>', content)
    return  (s or [], 
            HTMLParser.HTMLParser().unescape(n[0]))

def yt_get_url(z):
    return urllib.unquote(z['url'] + '&signature=%s' % z['sig'])

def youtube_video_link(url):
    # 18 - mp4
    fmt = '18'
    s, n = yt_get_all_url_maps_name(url)
    for z in s:
        if z['itag'] == fmt:
            if 'mp4' in z['type']:
                ext = '.mp4'
            elif 'flv' in z['type']:
                ext = '.flv'
            found = True
            link = yt_get_url(z)
    return link


def addLink(name,url,iconimage):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addNext(name,page,mode,iconimage):
    u=sys.argv[0]+"?url="+str(page)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
        
              
params=get_params()
url=None
name=None
mode=None

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

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
        ROOT()
       
elif mode==1:
        print ""+url
        FILME(url)
        
elif mode==2:
        print ""+url
        FILME_CALITATE_BUNA(url)

elif mode==3:
        print ""+url
        CAUTA(url)

elif mode==4:
        print ""+url+" si nume "+name
        VIDEO(url,name)

elif mode==5:
        print ""+url
        SERIALE(url)

elif mode==6:
        print ""+url
        SEZON(url)

elif mode==7:
        print ""+url
        EPISOADE(url)

elif mode==8:
        print ""+url
        VIDEO_EPISOD(url)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
                       
