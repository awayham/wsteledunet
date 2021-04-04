import cookielib
import re
import urllib2,urllib
from BeautifulSoup import BeautifulSoup
from models import ChannelItem
from hardcode import HARDCODED_STREAMS
print __name__

if __name__ != '__main__':
    import xbmcaddon
    selfAddon = xbmcaddon.Addon()
import time

HEADER_REFERER = 'http://www.teledunet.com/'
LOGIN_URL = 'http://www.teledunet.com/'
#TELEDUNET_CHANNEL_PAGE = 'http://www.teledunet.com/mobile/?con'
TELEDUNET_CHANNEL_PAGE = 'http://www.teledunet.com'

HEADER_HOST = 'www.teledunet.com'
HEADER_USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
#TELEDUNET_TIMEPLAYER_URL = 'http://www.teledunet.com/mobile/'
TELEDUNET_TIMEPLAYER_URL = 'http://www.teledunet.com/'
PPV_CHANNEL_URL='rtmp:/5.9.105.18:8080/live/'

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))


def _get(request,post=None):
    """Performs a GET request for the given url and returns the response"""
    return opener.open(request,post).read()

def _html(url, rheaders=None):
    """Downloads the resource at the given url and parses via BeautifulSoup"""
    headers = { "User-Agent": HEADER_USER_AGENT  }
    if rheaders:
        headers.update(rheaders);
    request = urllib2.Request (url , headers = headers)
    return BeautifulSoup(_get(request), convertEntities=BeautifulSoup.HTML_ENTITIES)


def __get_cookie_session():
    # Fetch the main Teledunet website to be given a Session ID
    _html('http://www.teledunet.com/')

    for cookie in cj:
        if cookie.name == 'PHPSESSID':
            return 'PHPSESSID=%s' % cookie.value

    raise Exception('Cannot find PHP session from Teledunet')

def performLogin():
    print 'performing login'
    userName=selfAddon.getSetting( "teledunetTvLogin" )
    password=selfAddon.getSetting( "teledunetTvPassword" )
    req = urllib2.Request(LOGIN_URL)
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
    post={'login_user':userName,'pass_user':password}
    post = urllib.urlencode(post)
    link = _get(req,post)

def __get_idu(html):
    userName=selfAddon.getSetting( "teledunetTvLogin" )
    id_patt = "idu_curent_user='(.*?)';"
#    id_patt = "id_user_rtmp='(.*?)';"
#    print str(html)
    idu = re.findall(id_patt, str(html))[0]
    return userName+idu
    
def __get_channel_time_player(channel_name):
    print 'in __get_channel_time_player'
    loginname=selfAddon.getSetting( "teledunetTvLogin" )
    ide = '_wcbstriu3x'
    mobileHtml=None
    if not (loginname==None or loginname==""):
        performLogin()

    id_patt = "id_user_rtmp='(.*?)';"

    try:
        post=None
        req = urllib2.Request('http://www.teledunet.com/')#access main page too
        req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
        _get(req,post)

        '''
        post=None
        req = urllib2.Request('http://www.teledunet.com/boutique/connexion6.php')#access main page too
        req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
        req.add_header('Referer','http://www.teledunet.com/')
        _get(req,post)
        '''
        post=None
        rnd=time.time()*1000
        post={'rndval':rnd}
        post = urllib.urlencode(post)
        req = urllib2.Request('http://www.teledunet.com/who_watch_channel.php?refresh=1')#access main page too
        req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
        req.add_header('Referer','http://www.teledunet.com/')
        html=_get(req,post)
        
        url = TELEDUNET_TIMEPLAYER_URL# % channel_name
        
        req = urllib2.Request(url)
        req.add_header('Referer', HEADER_REFERER)
        req.add_header('Host', HEADER_HOST)
        req.add_header('User-agent', HEADER_USER_AGENT)
        req.add_header('Cookie', __get_cookie_session())
        mobileHtml = _get(req)#dummycall
    except:
        print 'error in fetching time, using dummy value'
        raise
    
    url = TELEDUNET_TIMEPLAYER_URL# % channel_name
    print url

    
    if mobileHtml is None:
        req = urllib2.Request(url)
        req.add_header('Referer', HEADER_REFERER)
        req.add_header('Host', HEADER_HOST)
        req.add_header('User-agent', HEADER_USER_AGENT)
        req.add_header('Cookie', __get_cookie_session())
        html = _get(req)
    else:
        html=mobileHtml

    ide = __get_idu(html)
#    ide = re.findall(id_patt, html)[0]
    m = re.search('rtmp://(.*?)/%s\''%channel_name, html, re.M | re.I)
    if  m ==None:
        print 'geting from backup file'
        req = urllib2.Request("http://www.pastebin.com/download.php?i=fKh4gG5s")
        html = _get(req)
        m = re.search('rtmp://(.*?)/%s\''%channel_name, html, re.M | re.I)

    if  m ==None:
        rtmp_url=PPV_CHANNEL_URL+channel_name        
    else:
        rtmp_url = m.group(1)
        rtmp_url='rtmp://%s/?idu=%s'%(rtmp_url, ide)
    play_path = rtmp_url[rtmp_url.rfind("/") + 1:]

    rtmp_url = rtmp_url.replace('.net', '.com')
    '''    
    url1 = 'http://www.teledunet.com/rtmp_player/?channel=%(channel_name)s&streamer=%(rtmp_url)s' % {'channel_name': channel_name, 'rtmp_url' : rtmp_url}
    req = urllib2.Request(url1)
    req.add_header('Referer', HEADER_REFERER)
    req.add_header('Host', HEADER_HOST)
    req.add_header('User-agent', HEADER_USER_AGENT)
    req.add_header('Cookie', __get_cookie_session())
    html = _get(req)
    '''     
    return rtmp_url, ide # repr(time_player_str).rstrip('0').rstrip('.')


def get_rtmp_params(channel_name):
    rtmp_url, ide = __get_channel_time_player(channel_name)
    url1 = 'http://www.teledunet.com/rtmp_player/?channel=%(channel_name)s&streamer=%(rtmp_url)s' % {'channel_name': channel_name, 'rtmp_url' : rtmp_url}
#    url1 = 'http://www.teledunet.com/mobile/rtmp_player/?channel=%(channel_name)s&streamer=%(rtmp_url)s' % {'channel_name': channel_name, 'rtmp_url' : rtmp_url}
    url2 = 'http://www.teledunet.com/rtmp_player/?channel=%(channel_name)s' % {'channel_name': channel_name}
#    url2 = 'http://www.teledunet.com/mobile/rtmp_player/?channel=%(channel_name)s' % {'channel_name': channel_name}
    url3 = 'http://www.teledunet.com/rtmp_player/player.swf'
#    url3 = 'http://www.teledunet.com/mobile/rtmp_player/player.swf'
    patt_app = re.compile(r'live.*')
    url4 = patt_app.findall(rtmp_url)[0]
    return {
        'rtmp_url': rtmp_url,          # g
        'playpath': channel_name,
        'app': url4,                   # g
        'swf_url': url3,               # g
        'tc_url': rtmp_url,            # g
        'flash_ver': "WIN\\2025,0,0,127", # g
        'video_page_url': url1,        # g
        'live': '1'
    }
def update_idu():
    # login
    loginname = selfAddon.getSetting("teledunetTvLogin")
    if not (loginname == None or loginname == ""):
        performLogin()

    _html(HEADER_REFERER)

    headers = { "Referer": HEADER_REFERER  }
    html = _html(TELEDUNET_CHANNEL_PAGE, headers)

    # retrieve idu
    idu = __get_idu(html)
    return idu
    
def get_channels():
    #import pickle
    #import xbmc
    print 'get channels 1'
    loginname = selfAddon.getSetting("teledunetTvLogin")
    
    # login
    if not (loginname == None or loginname == ""):
        performLogin()
    print 'get channels 2'

#    _html(HEADER_REFERER)

    headers = { "Referer": HEADER_REFERER  }
    html = _html(TELEDUNET_CHANNEL_PAGE, headers)

    print 'get channels 3'
    # retrieve idu
    idu = __get_idu(html)
    
    channel_divs = lambda soup: (soup.findAll('div', id=re.compile(r'channel_\d+')))
    channel_divss = channel_divs(html)

    #xbmc.log(msg='Before divs count %d' % len(channel_divss), level=xbmc.LOGNOTICE)

    #xbmc.log(msg='After divs count %d' % len(channel_divss), level=xbmc.LOGNOTICE)
    #open(r'C:\Users\220554\logs\teledunet.html', 'wb').write(str(html))

    #F = open(r'C:\Users\220554\logs\chans_divs', 'wb')
    #pickle.dump(channel_divss, F)
    #F.write(str(channel_divss))
    channels = [ChannelItem(el=el) for el in channel_divss]
    print 'get channels 4'

    free_channels = []
#    free_patt = re.compile(r'\(name_channel ?== ?"(.+?)"')
    free_patt = re.compile(r"free_channels='(.+)'")
    #free_patt = re.compile(r'^\s*[^/]\|?\|?\(name_channel ?== ?"(.+?)"', flags = re.M)
    # in the above pattern
    # ^      : begin of line
    # \s     : This matches any whitespace character : [ \t\n\r\f\v]
    # [^/]   : that does not contain / for commented line
    # \|     : has | (twice)
    # has (name_channel == " with or without spaces
    # (.+?)  : this is what we capture the channel name that is not commented out
    # flags = re.M sets the string to be multi-line 
    

#    free_chans = free_patt.findall(str(html))
    match = free_patt.search(str(html))
    free_chans = match.group(1).split(',')
    free_chans.append('teledunet_tv')
    try:
        free_chans.remove('')
        free_chans.remove('')
    except:
        pass
    print free_chans
    for chan in channels:
        if chan.path in free_chans:
            chan.isFree = True
            free_channels.append(chan)
#            print '%s free chan'%chan.path
        else:
#            print chan.path
            chan.isFree = False
    return idu, channels


def __get_hardcoded_streams():
    return [ChannelItem(json=json) for json in HARDCODED_STREAMS]


def debug():
    idu, channels = get_channels()
    
    print 'idu = %s'%idu
    print 'chans count = %d' %len(channels)
    retdict = get_rtmp_params('teledunet_tv')
    print retdict
    pass


if __name__ == '__main__':
    class Addon:
        def __init__(self):
            print 'init Addon'
        def getSetting(self, var):
            if var == "teledunetTVLogin":
                retvar =  'tdn'
            elif var == "teledunetTVPassword":
                retvar = 'tdn'
            else:
                return ''
            return retvar
    selfAddon = Addon()
    debug()
