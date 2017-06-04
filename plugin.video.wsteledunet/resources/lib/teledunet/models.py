import re
#import xbmc

class ChannelItem:
    def __init__(self, el=None, json=None):
        if json is None:
            self.__parseElement(el)
        else:
            self.__parseJSON(json)

    def __parseElement(self, el):
        el = str(el)

        # retrieve title such as 'BBC arabic'
        pattern = r'(?:<span id="channel_name_\d+"\s+.*>)(.*)(?:</span>)'
        try:
            match_channel_name = re.findall(pattern, el)[0]
            self.title = match_channel_name
        except:
            open(r'C:\Users\220554\logs\chans', 'wb').write(str(el))
            return

        # retrieve thumbnail url
        self.thumbnail = re.findall('url\(\'(.*?)\'',el)[0]
        if ' ' in self.thumbnail:
            self.thumbnail=self.thumbnail.replace(' ','%20')
        if not self.thumbnail.startswith('http'): self.thumbnail = 'http://www.teledunet.com/' + self.thumbnail

        # retrieve path that is the channel name such as 'on_sport'
        self.path = re.findall('<input type="hidd.*?value="(.*?)\"',el)[0].split('/')[-1]
        
        # TBD retrieve isHD 
        self.isHD = False#len(anchorEl.findAll('font')) > 2

    def __parseJSON(self, json):
        self.title = json['title']
        self.thumbnail = json['thumbnail']
        if self.thumbnail: self.thumbnail=self.thumbnail.replace('tv_/icones','logo')
        if not self.thumbnail.startswith('http'): self.thumbnail='http://www.teledunet.com/'+self.thumbnail
        self.path = json['path']
        self.isHD = False

    def display_name(self):
        if self.isHD:
            return '%s [COLOR red]HD[/COLOR]' % self.title

        return self.title

