from scraper import (get_rtmp_params, get_channels, update_idu)
import xbmc
NETWORKS = {
    'Rotana': [],
    'Abu Dhabi': [],
    'Alarabiya': [],
    'Alhayat': [],
    'Aljazeera': ['JSC'],
    'CBC': [],
    'Dubai': [],
    'Dream': [],
    'MBC': [],
    'Panorama': [],
    'Persian': [],
    'Rotana': [],
    'Sama ': [],
    'Nile': [],
    'Melody': [],
    'Fox': [],
    'Al Nahar': ['Al-Nahar', 'Nahar']
}

CATEGORIES = {
    'Movies': ['Cinema', 'Aflam', 'Film', 'Cima'],
    'Drama': ['Series', 'Hekayat'],
    'Comedy': [],
    'Cooking': ['Fatafeat'],
    'Children': ['Ajyal', 'Baraem', 'Cartoon', 'Founon', 'Cocuk', 'Spacepower', 'Toyor'],
    'General': ['Alhayat', 'Dream', 'CBC', 'Faraeen', 'MBC Masr', 'MBC 1', 'MBC 3', 'MBC 4',
                'Masria', 'Masriya', 'Mehwar', 'Misr 25', 'Life', 'On TV', 'Ontv', 'Qatar', 'Dubai', 'Syria',
                'Sharjah'],
    'News': ['Alarabiya', 'Aljazeera', 'France', 'Geographic'],
    'Sport': ['riadia', 'Gladiator', 'JSC', 'Mosar3'],
    'Music': ['Aghanina', 'Hits', 'Zaman', 'Khaliji', 'Clip', 'Arabica', 'Ghinwa', 'Mawal', 'Mazzika', 'Mazeka', 'Melody Tv', 'Mtv', 'Zaman'],
    'Religion': ['Rahma', 'Anwar', 'Kawthar', 'Resala', 'Alnas', 'Coran', 'Iqra'],
    'English': ['Dubai One', 'Top Movies', 'MBC 2', 'Fx', 'MBC Action', 'MBC Drama', 'MBC Max', 'MBC Maghreb']
}

rtmp_base_url = r'rtmp://www.teledunet.com:1935'
swf_url = r'player.swf'
#swf_url = r'http://www.teledunet.com/rtmp_player/player.swf'
page_base_url = r'http://www.teledunet.com/rtmp_player/?channel='

'''The main API object. Useful as a starting point to get available subjects. '''


class TeledunetAPI(object):
    def __init__(self, cache):
        self.cache = cache

    def get_rtmp_params(self, channel_name):
        for chan in self.cache['all']:
            if channel_name == chan.path:
                channel_found = True
                break               # get out of loop once channel is found
            else:
                channel_found = False
        if channel_found:
            xbmc.log(msg='channel %s found in cache' % channel_name, level=xbmc.LOGNOTICE)
            
            if channel_name == 'teledunet_tv':
                app_str = r'live2/?idu=' + self.cache['idu']
            else:
                app_str = r'live/?idu=' + self.cache['idu']

            rtmp_url = rtmp_base_url + r'/' + app_str
            page_url = page_base_url + r'%s&streamer=%s' % (channel_name, rtmp_url)

            return {
                'rtmp_url'      : rtmp_url,            # g
                'playpath'      : channel_name,
                'file'          : channel_name,
                'app'           : app_str,             # g
                'swf_url'       : swf_url,             # g
                'tc_url'        : rtmp_url,            # g
                'flash_ver'     : "WIN\\2025,0,0,127", # g
                'video_page_url': page_url,            # g
                'live'          : '1'
                }
        else:    
            xbmc.log(msg='channel %s NOT found in cache' % channel_name, level=xbmc.LOGNOTICE)
            return get_rtmp_params(channel_name)

    def get_channels(self):
        if 'all' not in self.cache:
            self.update_channels()

        return self.cache.get('all')

    def get_free_channels(self):
        if 'all' not in self.cache:
            self.update_channels()

        free_chans = []
        
        for chan in self.cache['all']:
            if chan.isFree:
                 free_chans.append(chan)

        return free_chans

    def update_idu(self):
        idu = update_idu()
        self.cache['idu'] = idu

    def update_channels(self):
        idu, all = get_channels()
        self.cache['idu'] = idu
        self.cache['all'] = all
        
    def get_channels_grouped_by_network(self):
        items = []
        if 'all' not in self.cache:
            self.update_channels()
        channels = self.cache.get('all')

        for network in NETWORKS:
            children = self.get_channels_for_network(channels, network)
            items.append({
                'network_name': network,
                'label': '%(channel)s ([COLOR blue]%(count)s[/COLOR])' % {'channel': network, 'count': len(children)}
            })

        return items

    def get_channels_grouped_by_category(self):
        items = []

        if 'all' not in self.cache:
            self.update_channels()
        channels = self.cache.get('all')

        for category in CATEGORIES:
            children = self.get_channels_for_category(channels, category)
            items.append({
                'category_name': category,
                'label': '%(channel)s ([COLOR blue]%(count)s[/COLOR])' % {'channel': category, 'count': len(children)}
            })

        return items

    def get_channels_for_category(self, channels, channel_name):
        def __belongsToNetwork(channel):
            for prefix in CATEGORIES[channel_name]:
                if prefix in channel.title:
                    return True
            return channel_name in channel.title

        return filter(__belongsToNetwork, channels)

    def get_channels_for_network(self, channels, network_name):

        def __belongsToNetwork(channel):
            for prefix in NETWORKS[network_name]:
                if channel.title.startswith(prefix):
                    return True
            return channel.title.startswith(network_name)

        return filter(__belongsToNetwork, channels)