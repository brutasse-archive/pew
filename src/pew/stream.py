import asyncore
import re
import socket
import time

from htmlentitydefs import name2codepoint

try:
    import json
except ImportError:
    import simplejson as json

import oauth2 as oauth


def get_auth_header(consumer, token):
    oparams = {
        'oauth_version': '1.0',
        'oauth_nonce': oauth.generate_nonce(),
        'oauth_timestamp': int(time.time()),
        'oauth_token': token.key,
        'oauth_consumer_key': consumer.key,
    }

    req = oauth.Request(method="GET",
                        url="http://chirpstream.twitter.com/2b/user.json",
                        parameters=oparams)

    signature_method = oauth.SignatureMethod_HMAC_SHA1()
    req.sign_request(signature_method, consumer, token)

    return 'Authorization: %s' % req.to_header()['Authorization']

# Font colors #
BLACK = '\x1b[30m'
RED = '\x1b[31m'
GREEN = '\x1b[32m'
YELLOW = '\x1b[33m'
BLUE = '\x1b[34m'
PURPLE = '\x1b[35m'
PALE_BLUE = '\x1b[36m'
WHITE = '\x1b[37m'

# Background colors #
RED_BG = '\x1b[41m'
GREEN_BG = '\x1b[42m'
YELLOW_BG = '\x1b[43m'
BLUE_BG = '\x1b[44m'
PURPLE_BG = '\x1b[45m'
PALE_BLUE_BG = '\x1b[46m'
WHITE_BG = '\x1b[47m'

# Font effects #
BOLD = '\033[1m'
ITALICS = '\033[3m'
UNDERLINE = '\033[4m'
BLINK = '\033[5m'
HIGHIGHTED = '\033[7m'

# Reset #
END = '\033[0m'

HASH_RE = re.compile(r"(?P<start>.?) #(?P<hashtag>[A-Za-z0-9_]+)(?P<end>.?)")
HASH_RE2 = re.compile(r"^#(?P<hashtag>[A-Za-z0-9_]+)(?P<end>.?)")
USERNAME_RE = re.compile(r"(?P<start>.?)@(?P<user>[A-Za-z0-9_]+)(?P<end>.?)")


def _replace_entity(match):
    text = match.group(1)
    if text[0] == u'#':
        text = text[1:]
        try:
            if text[0] in u'xX':
                c = int(text[1:], 16)
            else:
                c = int(text)
            return unichr(c)
        except ValueError:
            return match.group(0)
    else:
        try:
            return unichr(name2codepoint[text])
        except (ValueError, KeyError):
            return match.group(0)

_entity_re = re.compile(r"&(#?[xX]?(?:[0-9a-fA-F]+|\w{1,8}));")


def unescape(text):
    return _entity_re.sub(_replace_entity, text)


def twitterfy(tweet, effect=BLUE + UNDERLINE):
    link = r'\g<start> ' + effect + r'#\g<hashtag>' + END + r'\g<end>'
    tweet = HASH_RE.sub(link, tweet)
    link = effect + r'#\g<hashtag>' + END + r'\g<end>'
    tweet = HASH_RE2.sub(link, tweet)

    link = r'\g<start>' + effect + r'@\g<user>' + END + r'\g<end>'
    return USERNAME_RE.sub(link, tweet)


def process(tweet):
    return twitterfy(unescape(tweet))


def username(text):
    return GREEN + text + END


def contextual(text):
    return '\n\t' + PURPLE + text + END


def retweeted_by(user):
    return contextual('Retweeted by ' + user)


class StreamClient(asyncore.dispatcher):

    def __init__(self, host, headers):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, 80))
        self.buffer = '\r\n'.join(headers) + '\r\n\r\n'
        self.data = ''

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        self.data += self.recv(8192)
        if not self.data.endswith('\r\n\r\n'):
            return

        data = self.data.split('\r\n')

        if len(data) > 4:
            data = data[-5:]
        content = data[1]
        if not content:
            self.data = ''
            return

        try:
            payload = json.loads(content)
        except ValueError:
            print 'Unable to load data: %s' % content
            return

        if type(payload) == int:
            self.data = ''
            return

        self.handle_json(payload)
        self.data = ''

    def writable(self):
        return len(self.buffer) > 0

    def write(self, data):
        self.buffer += data

    def handle_write(self):
        sent = self.send(self.buffer)
        self.buffer = self.buffer[sent:]

    def handle_json(self, payload):
        message = json.dumps(payload, indent=2)

        if 'text' in payload:
            message = '%s: %s' % (username(payload['user']['screen_name']),
                                  process(payload['text']))

            if 'retweeted_status' in payload:
                usrname = payload['retweeted_status']['user']['screen_name']
                params = (username(usrname),
                          process(payload['retweeted_status']['text']))
                message = '%s: %s' % params
                message += retweeted_by(payload['user']['screen_name'])

        elif 'event' in payload:
            if payload['event'] in ('list_member_added',
                                    'list_member_removed'):
                action = payload['event'].replace('list_member_', '')
                prep = 'to'
                if action == 'removed':
                    prep = 'from'
                params = (username(payload['source']['screen_name']),
                          action,
                          username(payload['target']['screen_name']),
                          prep,
                          username(payload['target_object']['name']))
                message = '%s %s %s %s his %s list' % params

            elif payload['event'] == 'follow':
                params = (username(payload['source']['screen_name']),
                          username(payload['target']['screen_name']))
                message = '%s is following %s' % params

            elif payload['event'] in ('favorite', 'unfavorite'):
                params = (username(payload['source']['screen_name']),
                          payload['event'],
                          username(payload['target']['screen_name']),
                          process(payload['target_object']['text']))
                message = '%s %sd %s: %s' % params

            elif payload['event'] == 'list_created':
                params = (username(payload['source']['screen_name']),
                          username(payload['target_object']['name']))
                message = '%s created a list: %s' % params
                message += contextual(payload['target_object']['description'])

            elif payload['event'] == 'list_updated':
                params = (username(payload['source']['screen_name']),
                          username(payload['target_object']['name']))
                message = '%s updated his %s list' % params
                message += contextual(payload['target_object']['description'])

            elif payload['event'] == 'list_destroyed':
                params = (username(payload['source']['screen_name']),
                          username(payload['target_object']['name']))
                message = '%s deleted his %s list' % params

        elif 'friends' in payload:
            message = 'You\'ve got %s friends' % len(payload['friends'])

        elif 'direct_message' in payload:
            usrname = payload['direct_message']['sender_screen_name']
            params = (username(usrname),
                      process(payload['direct_message']['text']))
            message = YELLOW + 'DM from' + END + ' %s: %s' % params

        print message
        print


def main(config):
    token = oauth.Token(secret=config['token_secret'],
                        key=config['token_key'])

    consumer = oauth.Consumer(key=config['consumer_key'],
                              secret=config['consumer_secret'])
    host = 'chirpstream.twitter.com'

    headers = [
        'GET /2b/user.json HTTP/1.1',
        'Host: %s' % host,
        get_auth_header(consumer, token),
    ]

    c = StreamClient(host, headers)
    asyncore.loop()


def client(config):
    while True:
        try:
            main(config)
        except KeyboardInterrupt:
            print "Bye!"
            return
        except:
            pass
