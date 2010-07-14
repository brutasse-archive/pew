import os.path

from configobj import ConfigObj

import stream


def main():
    config_file = os.path.join(os.path.expanduser('~'), '.pewrc')
    config = ConfigObj(config_file)
    if not config:
        oauth_config = {
            'consumer_key': '',
            'consumer_secret': '',
            'token_key': '',
            'token_secret': '',
        }

        config['OAuth'] = oauth_config
        config.write()

    key, secret = (config['OAuth']['consumer_key'],
                   config['OAuth']['consumer_secret'])
    if not all((key, secret)):
        print "No consumer key or secret found. Put them in %s" % config_file
        return

    key, secret = config['OAuth']['token_key'], config['OAuth']['token_secret']
    if not all((key, secret)):
        print "No token key or secret found. Put them in %s" % config_file
        return

    stream.client(config['OAuth'])


if __name__ == '__main__':
    main()
