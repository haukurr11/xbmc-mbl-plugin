#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright 2012 Haukur Rosinkranz. 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import urllib,urllib2,re,xbmcplugin,xbmcgui
try:
    import json
except ImportError:
    import simplejson as json

mobilepage = "http://m.mbl.is"
mainpage = "http://mbl.is"
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
default_icon = mainpage + '/img/hauslogo/mbl.generic.png' 

##HELPING FUNCTIONS START

#gets input from the keyboard
def keyboardinput():
	user_keyboard = xbmc.Keyboard()
	user_keyboard.doModal()
	return user_keyboard.getText()

#error message when videos cannot be found (looks better than a dialog imo)
def mbl_error():
	addDir("Villa, ekkert fannst","",'show',"")

#tweak video links to work on the mobile version of mbl(speedboost)
def mobilize_link(link):
	try:
		return "/sjonvarp/helstu/" + link[len(link)-6:][:5]
	except:
		return ""

#makes a direct link to a video
def videolink(name,link,thumbnail):
	try:
		videolink = get_html(mobilepage+link)
		direct_vlink=re.search('file:"(.+?)"',videolink).group(1)
		addLink(name,direct_vlink,thumbnail)
	except:
		pass

#gets html of an url
def get_html(url):
	request = urllib2.Request(url)
	request.add_header('User-Agent',user_agent)
	response = urllib2.urlopen(request)
	html_source=response.read()
	response.close()
	return html_source

#cleans up html strings(removes special letters)
def html_fixup(code):
	code = code.replace("&amp;","&").replace("&#34;",'"')
	remove_special_letters = re.compile('[&].+?[;]')
	return remove_special_letters.sub("",code)
	
##MAIN FUNCTIONS START

#the main page
def index_page():
	addDir("Leita...","leitarvel",'startsearching',default_icon)
	tv = "/sjonvarp"
	firstpage = "/?page=0"
	addDir("Helstu fr\xc3\xa9ttir",mobilepage + tv + firstpage,'mobile',default_icon)
	link = get_html(mobilepage + tv)
	try: #get all the categories from the mobile version of mbl
		navigation=re.search('<p id="sjonvarp-banner">(.+?)</p>',link,re.DOTALL).group(1)
		categories=re.compile('<a href="(.+?)">(.+?)</a>',re.DOTALL).findall(navigation)
		for link,title in categories:
			addDir(title,mobilepage + link + firstpage,'mobile',default_icon)
	except:
		pass
	addDir("Mest sko\xc3\xb0a\xc3\xb0","mestskodad",'mostviewed',default_icon)
	addDir("Þ\xc3\xa6ttir","thaettir",'showlist',default_icon)

#ask user for input and start the search
def mbl_startsearch():
	searchword = keyboardinput()
	mbl_search(searchword + "{1}")

#input: "word to search for"{pagenumber}
#output: search results at the page given
def mbl_search(searchword_and_page):
	searchword = searchword_and_page[:searchword_and_page.find("{")]
	page = searchword_and_page[searchword_and_page.find("{")+1:searchword_and_page.find("}")]
	nextpage = int(page)+1
	if searchword:
		try:
			html_source = get_html(mainpage + "/frettir/sjonvarp/search/?page=" + str(page) + "&qs=" + searchword.replace(" ","%20") + "&sort_by_date=0")
			if '<p class="warning">Ekkert fannst</p>' not in html_source:
				html_source = html_source.split('<div class="searchresults" id="searchresults">')[1] #reduce the html needed to regex search
				addDir("("+str(page)+")" + "N\xc3\xa6sta s\xc3\xad\xc3\xb0a>>",searchword + "{" + str(nextpage) + "}",'search',default_icon)
				results=re.compile('<a href="(.+?)".+?title="(.+?)".+?class="video_ajax">.+?<img src="(.+?)".+?alt=".+?" />',re.DOTALL).findall(html_source)
				for link,name,thumbnail in results:
					videolink(html_fixup(name),mobilize_link(link),mobilepage+thumbnail)
			else:
				mbl_error()
		except:
			mbl_error()

#all pages from the mobile site
def mobile_site(url):
	html_source = get_html(url)
	results=re.compile('<h4>(.+?)</h4>.+?<a href="(.+?)"><img src="(.+?)" alt=".+?" /></a>',re.DOTALL).findall(html_source)
	nextpage_nr = int(url[1+url.find("="):])+1 #the number that comes after the "=" in the url is the page number we are at
	addDir("(" + str(nextpage_nr) + ") N\xc3\xa6sta s\xc3\xad\xc3\xb0a>>",url[:url.find("=")+1] + str(nextpage_nr),'mobile',default_icon)
	for name,link,thumbnail in results:
		videolink(name,link,mobilepage+thumbnail)
		
#most viewed videos
def mostviewed():
	html_source = get_html(mainpage + "/sjonvarp/")
	try:
		new_shows=re.search('<div id="most_viewed">(.+?)<div id="searchbox">',html_source,re.DOTALL).group(1)
		results=re.compile('<li.+?<a href="(.+?)".+?title="(.+?)".+?<img src="(.+?)"',re.DOTALL).findall(new_shows)
		for link,name,thumbnail in results:
			videolink(name,mobilize_link(link),mainpage+thumbnail)
	except:
		mbl_error()

#list of episode series on mbl
def list_of_series():
	html_source = get_html(mainpage + "/frettir/sjonvarp/thaettir/")
	try:
		new_shows=re.search('<div id="mbl_thaettir">(.+?)<div class="nyir_thaettir">',html_source,re.DOTALL).group(1)
		results=re.compile('<div class="img">.+?/frettir/sjonvarp/thaettir/(.+?)/"><img alt="(.+?)" src="(.+?)"',re.DOTALL).findall(new_shows)
		for link,name,thumbnail in results:
			addDir(html_fixup(name),mainpage + "/frettir/sjonvarp/more_thaettir/?keyword=" + link + "&offset=0&limit=9999",'show',mainpage+thumbnail)
	except:
		mbl_error()

#list of episodes in each series
def series(url):
	json_info = get_html(url)
	json_to_html = unicode(json.loads(json_info)).encode("utf-8")
	list_of_shows=re.compile('<div class=\"item\">.+?<div class=\"img\">.+?<a href=\"(.+?)"><img alt=\"(.+?)" src=\"(.+?)"/></a>.+?</div>.+?<div class=\"date\">.+?<span class=\"gray\">(.+?)</span>',re.DOTALL).findall(json_to_html)
	for link,name,thumbnail,date in list_of_shows:
		exec 'name =  u"%s".encode("utf-8")' % (name) #fix up the encoding
		videolink(html_fixup(name),mobilize_link(link),mainpage+thumbnail)
	
##PARAMETER PROCESSING STARTS
def addLink(name,url,iconimage):
	ok=True
	liz=xbmcgui.ListItem(name, iconImage=default_icon, thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
	return ok

def addDir(name,url,mode,iconimage):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url) + "&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage=default_icon, thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
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

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=str(params["mode"])
except:
        pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
        print ""
        index_page()
       
elif mode=='mobile':
        print ""+url
        mobile_site(url)
elif mode=='show':
        print ""+url
        series(url)
elif mode=='showlist':
        print ""+url
        list_of_series()
elif mode=='mostviewed':
        print ""+url
        mostviewed()
elif mode=='startsearching':
        print ""+url
        mbl_startsearch()
elif mode=='search':
        print ""+url
        mbl_search(url)
		
xbmcplugin.endOfDirectory(int(sys.argv[1]))
