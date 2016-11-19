import configparser
import os.path
import xdg.BaseDirectory

class Config:
    def __init__(self):
        cfg = configparser.ConfigParser()

        with open(os.path.join(xdg.BaseDirectory.load_first_config("deenes"), 'deenes.conf'), 'r') as cfgfile:
            cfg.read_file(cfgfile)
            self.apikey = cfg.get(section='api', option='apikey')
            self.hostname = cfg.get(section='api', option='hostname')
            self.interface = cfg.get(section='api', option='interface')
