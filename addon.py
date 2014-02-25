"""
    990.ro XBMC Addon
    Copyright (C) 2012-2014 krysty
	https://code.google.com/p/krysty-xbmc/

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import sys, os, time, string
import urllib, urllib2
import re
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
from resources.lib.BeautifulSoup import BeautifulSoup
import HTMLParser
from resources.lib.ga import track


siteUrl = 'http://www.990.ro/'
searchUrl = 'http://www.990.ro/functions/search3/live_search_using_jquery_ajax/search.php'


addonId = 'plugin.video.990'
selfAddon = xbmcaddon.Addon(id=addonId)
pluginPath = xbmc.translatePath(selfAddon.getAddonInfo('path'))

USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
ACCEPT = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'

TVshowsIcon = os.path.join(pluginPath, 'resources', 'media', 'tvshowsicon.png')
MoviesIcon = os.path.join(pluginPath, 'resources', 'media', 'moviesicon.png')
SearchIcon = os.path.join(pluginPath, 'resources', 'media', 'searchicon.png')
InfoIcon = os.path.join(pluginPath, 'resources', 'media', 'inficon.png')

track()



def CATEGORIES():
	addDir('Seriale TV ',siteUrl,4,TVshowsIcon)
	addDir('Filme',siteUrl,10,MoviesIcon)
	addDir('Cauta',siteUrl,22,SearchIcon)


def TVSHOWSORDER(url):
	AZ = (ltr for ltr in string.ascii_uppercase)
	
	addDir('Toate',url,1,TVshowsIcon)
	addDir('Ultimele aduse',url,5,TVshowsIcon)
	addDir('Cauta',url,21,TVshowsIcon)
	addDir('1-9',url,30,TVshowsIcon)
	for character in AZ:
		addDir(character,url,30,TVshowsIcon)
	

def get_tvshows(url,order=""):

	progress = xbmcgui.DialogProgress()
	progress.create('Progress', 'Asteptati...')
	
	soup = BeautifulSoup(http_req(url))
	div = htmlFilter(str(soup.find("div", {"id": "sub1"})))
		
	if order:
		match = re.compile('href="seriale-(.+?)-online-download\.html" title=".+?">(['+order+'].+?)</a>').findall(div)
	else:
		match = re.compile('href="seriale-(.+?)-online-download\.html" title=".+?">(.+?)</a>').findall(div)
	
	count = 1
	current = 0
	total = len(match)
	
	while not progress.iscanceled() and current <= total - 1:
		addDir(str(count)+'. '+match[current][1],url+'seriale-'+match[current][0]+'-online-download.html',2,'')
		current = current + 1
		
		percent = int( ( count * 100 ) / total)
		message = "Incarcare seriale tv " + str(count) + " of " + str(total)
		progress.update(percent, "", message, "")
		
		count = count + 1
		
	notif('TV Shows',str(total)+' found')
	
	progress.close()

		
def get_tvshow_seasons(name, url):

	progress = xbmcgui.DialogProgress()
	progress.create('Progress', 'Asteptati...')
	
	match = re.compile('<img src=\'.+?\' alt=\'Sezonul (.+?)\'>').findall(http_req(url))
	thumb = re.compile('<img src=\'../(.+?)\'').findall(http_req(url))
	if thumb: videothumb = siteUrl+thumb[0]
	else: videothumb = ''
	
	total = len(match)
	count = 1
	
	while not progress.iscanceled() and count <= total:

		for season_number in match:
			addDir('Sezon '+str(season_number).zfill(2),url,3,videothumb,name,videothumb)
		
			percent = int( ( count * 100 ) / total)
			message = "Incarcare sezon " + str(count) + " of " + str(total)
			progress.update( percent, "", message, "" )
			if progress.iscanceled(): sys.exit()
			
			count = count + 1
			
	progress.close()

		
def get_tvshow_episodes(tvshow_url,season,videoname,videothumb):
	
	progress = xbmcgui.DialogProgress()
	progress.create('Progress', 'Asteptati...')
	
	soup = BeautifulSoup(http_req(url))
	div = htmlFilter(str(soup.find("div", {"id": "content"})), True)
	
	m = re.search('[\d]+', season)
	season = m.group(0)
	
	episodes = re.compile('Sezonul '+season+', Episodul (.+?)</div>.+?<a href="seriale2-([\d]+-[\d]+)-.+?\.html" class="link">(.+?)</a>').findall(div)
	
	if episodes:
		total = len(episodes)
	else:
		episodes = re.compile('ma;">([\d]+)</div>.+?<a href="seriale2-([0-9]+-[0-9]+)-.+?\.html" class="link">(.+?)</a>').findall(div)
		total = len(episodes)
	
	count = 1
	
	while not progress.iscanceled() and count <= total:
			
		for ep_num, ep_href, ep_name in episodes:
			if ep_name == str(re.findall('(Episodul [-0-9]*)',ep_name)).strip('[]').strip('"\''): ep_name = ""
			
			addDir('Episod '+ep_num+' '+ep_name,siteUrl+'player-serial-'+ep_href+'-sfast.html',8,videothumb,videoname,videothumb)
			
			percent = int( ( count * 100 ) / total)
			message = "Incarcare episod " + str(count) + " of " + str(total)
			progress.update(percent, "", message, "")
			if progress.iscanceled(): sys.exit()
			
			count = count + 1
	
	progress.close()
	

def last_added(cat):

	progress = xbmcgui.DialogProgress()
	progress.create('Progress', 'Asteptati...')

	soup = BeautifulSoup(http_req(siteUrl))
	div = htmlFilter(str(soup.find("div", {"id": "tab1"})), True)
	
	if cat == 'seriale':
		match = re.compile('<a class="link" href="(seriale2)-([0-9]+-[0-9]+)-.+?\.html">(.+?)</a>([0-9 a-z]+)</div>.+?">(.+?)</div>').findall(div)
	elif cat == 'filme':
		match = re.compile('<a class="link" href="(filme)-(.+?)\.html">(.+?)</a>([0-9 a-z]+)</div>.+?">(.+?)</div>').findall(div)
	
	total = len(match)
	count = 1
	
	while not progress.iscanceled() and count <= total:
			
		for type, link, name, since, ep_year in match:
			
			if type == 'seriale2':
				addDir(ep_year+' '+name+' ['+ro2en(since)+']',siteUrl+'player-serial-'+link+'-sfast.html',8,"",ep_year+' '+name,"")
			elif type == 'filme':
				addDir(name+' ('+ep_year+') ['+ro2en(since)+']',siteUrl+'filme-'+link+'.html',8,"",name+' ('+ep_year+')',"")

			percent = int( ( count * 100 ) / total)
			message = "Incarcare item " + str(count) + " of " + str(total)
			progress.update(percent, "", message, "")
			if progress.iscanceled(): sys.exit()
			
			count = count + 1
	
	progress.close()
	

def MOVIESORDER(url):
        addDir('Dupa gen',url,12,MoviesIcon)
        addDir('Dupa an',url,11,MoviesIcon)
	addDir('Ultimele aduse',url,6,MoviesIcon)
	addDir('Cauta',url,20,MoviesIcon)
	
	


def MOVIESbyYEAR(url):
	match = re.compile('<a href="filme2-(.+?)" title="[0-9]+">Filme (.+?)</a>').findall(http_req(url))
	for link, year in match:
		addDir(str(year),url+'filme2-'+link,9,MoviesIcon)


def MOVIESbyGENRE(url):
	match = re.compile('<a href="filme-(.+?)" title=".+?">(.+?)</a>').findall(http_req(url))
	for link, genre in match:
		addDir(str(ro2en(genre)),url+'filme-'+link,9,MoviesIcon)


def get_movies(url):

	progress = xbmcgui.DialogProgress()
	progress.create('Progress', 'Asteptati...')

	soup = BeautifulSoup(http_req(url))
	div = str(soup.find("div", {"id": "numarpagini"}))
	match = re.compile('([\d]+)</a>').findall(div)
	pages = [int(x) for x in match]
	maxpage = max(pages)
	
	count = 1
	page = 1
	total_movies = ""

	while not progress.iscanceled() and count < total_movies:
	
		while not progress.iscanceled() and page <= maxpage:
			url = re.sub('-\d\.+', '-'+str(page)+'.', url)

			soup = BeautifulSoup(http_req(url))
			div = htmlFilter(str(soup.find("div", {"id": "content"})))
			match = re.compile('<a href="filme-(.+?)-online-download\.html" .+? class="link">(.+?)</a> \(([\d]+)\)').findall(div)
			thumb = re.compile('<img src="../(.+?)"').findall(div)
			
			current = 0
			total_movies = len(match) * maxpage

			while not progress.iscanceled() and current <= len(match) - 1:
				name = str(count)+'. '+match[current][1]+' ('+match[current][2]+')'
				link = siteUrl+'filme-'+match[current][0]+'-online-download.html'
				image = siteUrl+thumb[current]
				videoname = re.sub('[0-9]+\. ', "", name)
				
				addDir(name,link,8,image,videoname,image)
				
				current = current + 1
				
				percent = int( ( count * 100 ) / total_movies)
				if page == maxpage: percent = 100
				message = "Loading list - " + str(percent) + "%"
				progress.update(percent, "", message, "")
				if progress.iscanceled(): sys.exit()
				
				count = count + 1
			
			page = page + 1
		
		notif('Filme',str(count - 1)+' gasite')
	
	progress.close()


def get_video(url,videoname,videothumb):
	
	progress = xbmcgui.DialogProgress()
	progress.create('Progress', 'Asteptati...')
	
	quality = ''
	
	if(re.search('filme', url)):
		quality = re.compile('Calitate film: nota <b>(.+?)</b>').findall(http_req(url))
		movieId = re.search('-([\d]+)-', url)
		movieId = movieId.group(1)
		
		match = re.compile('<iframe width=\'595\' height=\'335\' src=\'.+?\/embed\/(.+?)\'').findall(http_req(url))
		if match:
			trailer_link = youtube_video('http://www.youtube.com/watch?v='+match[0])
		else:
			trailer_link = False
			
		if trailer_link:
			addLink('Play Trailer', trailer_link+'?.mp4', videothumb, 'Trailer '+videoname)
			
		url = siteUrl+'player-film-'+movieId+'-sfast.html'
	
	i = 1
	
	while not progress.iscanceled() and i < 2:
		try:
			match = re.compile('http:\/\/fastupload\.?r?o?l?\.ro\/?v?i?d?e?o?\/(.+?)\.html').findall(http_req(url))
			url = 'http://superweb.rol.ro/video/'+match[0]+'.html'
			match = re.compile('\'file\': \'(.+?)\',').findall(http_req(url))
			videoLink = match[0]+'|referer='+url
			if(quality == ''):
				addLink('Deschide Video',videoLink,videothumb,videoname)
			else:
				addLink('Deschide Video (Quality:'+quality[0]+')',videoLink,videothumb,videoname)
			
			percent = int( ( i / 2.0 ) * 100)
			message = "Incarca video..."
			progress.update(percent, "", message, "")

			i = i + 1
			
		except:
			message = "Eroare: link indisponibil!"
			progress.update(100, "", message, "")
			time.sleep(2)
			sys.exit()
	
	progress.close()
	

def SEARCH(cat):

	kb = xbmc.Keyboard('', 'Cauta', False)
	kb.doModal()
	if (kb.isConfirmed()):
		searchText = kb.getText()
		if searchText == '':
			dialog = xbmcgui.Dialog().ok('Cauta','Nu este nimic de cautat.')
			xbmc.executebuiltin('Notification(Nu este nimic de cautat.,Va rugam introduceti alta cautare.,5000)')
			sys.exit()
		else:
			progress = xbmcgui.DialogProgress()
			progress.create('Progress', 'Asteptati...')
			
			values = {'kw': searchText}
			data = urllib.urlencode(values)
			req = urllib2.Request(searchUrl, data, headers = {'User-Agent': USER_AGENT})
			response = htmlFilter(urllib2.urlopen(req).read())
			
			if cat == 'all':
				match = re.compile('<a href="(.+?)-(.+?)-online-download\.html">.+?<div id="rest">(.+?)<div id="auth_dat">').findall(response)
				thumb = re.compile('<img class="search" .+? src="../(.+?)"').findall(response)
			else:
				match = re.compile('<a href="('+cat+')-(.+?)-online-download\.html">.+?<div id="rest">(.+?)<div id="auth_dat">').findall(response)
				thumb = re.compile('<a href="'+cat+'-.+?<img class="search" .+? src="../(.+?)"').findall(response)
			
			total = len(match)
			count = 1
			
			while not progress.iscanceled() and count <= total:

				current = 0
				
				while not progress.iscanceled() and current <= total - 1:
					
					if match[current][0] == 'seriale':					
						name = re.sub('\(', ' (', str(count)+'. '+match[current][2])
						url = siteUrl+'seriale-'+match[current][1]+'-online-download.html'
						image = siteUrl+thumb[current]
						videoname = re.sub('[0-9]+\. ', "", name)
						
						addDir(name,url,2,image,videoname,image)
					
					elif match[current][0] == 'filme':						
						name = re.sub('\(', ' (', str(count)+'. '+match[current][2])
						url = siteUrl+'filme-'+match[current][1]+'-online-download.html'
						image = siteUrl+thumb[current]
						videoname = re.sub('[0-9]+\. ', "", name)
						
						addDir(name,url,8,image,videoname,image)
					
					current = current + 1

					percent = int( ( count * 100 ) / total)
					message = "Incarcare " + str(count) + " din " + str(total)
					progress.update( percent, "", message, "" )
					
					count = count + 1
				
				notif('Cautare',str(total)+' gasite')
			
			progress.close()
	
	else: sys.exit()


def notif(title,message):
	notification = xbmc.executebuiltin('Notification('+title+','+message+',2000,'+InfoIcon+')')
	return notification


def get_params():
	param = []
	paramstring = sys.argv[2]
	if len(paramstring) >= 2:
			params = sys.argv[2]
			cleanedparams = params.replace('?','')
			if (params[len(params)-1] == '/'):
				params = params[0:len(params)-2]
			pairsofparams = cleanedparams.split('&')
			param = {}
			for i in range(len(pairsofparams)):
				splitparams = {}
				splitparams = pairsofparams[i].split('=')
				if (len(splitparams)) == 2:
					param[splitparams[0]] = splitparams[1]
	return param



def http_req(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', USER_AGENT)
	req.add_header('Accept', ACCEPT)
	response = urllib2.urlopen(req)
	source = response.read()
	response.close()
	return source

	
def youtube_video(url):
	conn = urllib2.urlopen(url)
	encoding = conn.headers.getparam('charset')
	content = conn.read().decode(encoding)
	s = re.findall(r'"url_encoded_fmt_stream_map": "([^"]+)"', content)
	if s:
		s = s[0].split(',')
		s = [a.replace('\\u0026', '&') for a in s]
		s = [urllib2.parse_keqv_list(a.split('&')) for a in s]	
	n = re.findall(r'<title>(.+) - YouTube</title>', content)
	s, n = (s or [], HTMLParser.HTMLParser().unescape(n[0]))
	for z in s:
		if z['itag'] == '18':
			if 'mp4' in z['type']:
				ext = '.mp4'
			elif 'flv' in z['type']:
				ext = '.flv'
			found = True
			link = urllib.unquote(z['url'] + '&signature=%s' % z['sig'])
	return link
	

def addLink(name,url,iconimage,videoname):
	ok = True
	liz = xbmcgui.ListItem(name, iconImage = "DefaultVideo.png", thumbnailImage = iconimage)
	liz.setInfo(type="Video", infoLabels = {"Title": videoname})
	ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]),url = url, listitem = liz)
	return ok

	
def addDir(name,url,mode,iconimage,videoname='',videothumb=''):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&videoname="+urllib.quote_plus(videoname)+"&videothumb="+urllib.quote_plus(videothumb)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels = {"Title": name})
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url = u,listitem = liz, isFolder = True)
	return ok

	
def htmlFilter(htmlstring, trimspaces = False):
	hex_entity_pat = re.compile('&#x([^;]+);')
	hex_entity_fix = lambda x: hex_entity_pat.sub(lambda m: '&#%d;' % int(m.group(1), 16), x)
	htmlstring = str(BeautifulSoup(hex_entity_fix(htmlstring), convertEntities=BeautifulSoup.ALL_ENTITIES))
	if trimspaces:
		htmlstring = "".join(line.strip() for line in htmlstring.split("\n"))
	return htmlstring


def ro2en(string):
	
	dict = {
			'Actiune':		'Actiune',
			'Animatie':		'Desene animate',
			'Aventura':		'Aventura',
			'Biografie':	'Biografie',
			'Comedie':		'Comedie',
			'Crima':		'Crima',
			'Documentar':	'Documentare',
			'Dragoste':		'Dragoste',
			'Familie':		'Familie',
			'Fantezie':		'Fantezie',
			'Istorie':		'Istorie',
			'Mafie':		'Mafie',
			'Mister':		'Mister',
			'Razboi':		'Razboi',
			'Sarbatori':	'Sarbatori',
			'S.F.':			'Sci-Fi',
			'cateva ore':	'cateva ore',
			'ore':			'ore',
			'o ora':		'1 ora',
			'o zi':			'1 zi',
			'o saptamana':	'1 saptamana',
			'o luna':		'1 luna',
			'zile':			'zile',
			'saptamani':	'saptamani',
			'luni':			'luni'
	}
	
	try:	
		string = string.strip()
		string = re.compile(r'\b(' + '|'.join(dict.keys()) + r')\b').sub(lambda x: dict[x.group()], string)
	except:
		pass
	
	return string


params = get_params()
url = None
name = None
mode = None
videoname = ""
videothumb = ""

try:
	url = urllib.unquote_plus(params["url"])
except:
	pass
try:
	name = urllib.unquote_plus(params["name"])
except:
	pass
try:
	mode = int(params["mode"])
except:
	pass
try:
	videoname = urllib.unquote_plus(params["videoname"])
	videoname = re.sub('[0-9]+\.',"",videoname)
except:
	pass
try:
	videothumb = urllib.unquote_plus(params["videothumb"])
except:
	pass


print "Mode: "+str(mode)
print "URL: "+str(url)


if mode == None or url == None or len(url) < 1:
	CATEGORIES()
       
elif mode == 1:
	get_tvshows(url)

elif mode == 2:
	get_tvshow_seasons(name,url)
		
elif mode == 3:
	get_tvshow_episodes(url,name,videoname,videothumb)

elif mode == 4:
	TVSHOWSORDER(url)
	
elif mode == 5:
	last_added('seriale')
	
elif mode == 6:
	last_added('filme')

elif mode == 8:
	print ""+url
	get_video(url,videoname,videothumb)
	
elif mode == 9:
	get_movies(url)
	
elif mode == 10:
	MOVIESORDER(url)
	
elif mode == 11:
	MOVIESbyYEAR(url)

elif mode == 12:
	MOVIESbyGENRE(url)

elif mode == 20:
	SEARCH('filme')
	
elif mode == 21:
	SEARCH('seriale')

elif mode == 22:
	SEARCH('all')

elif mode == 30:
	get_tvshows(url,name)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
