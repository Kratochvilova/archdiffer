# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 22:18:26 2017

@author: Pavla Kratochvilova <pavla.kratochvilova@gmail.com>
"""

from ..config import config

def get_openid_providers():
    providers = {}
    for section in config.sections():
        if section.startswith('openid'):
            providers[config[section]['NAME']] = config[section]['URL']
    return providers

class FlaskConfig(object):
    DEBUG = config['web']['DEBUG']
    SECRET_KEY = config['web']['SECRET_KEY']
    OPENID_FS_STORE_PATH = config['web']['OPENID_FS_STORE_PATH']
    API_TOKEN_LENGTH = int(config['web']['API_TOKEN_LENGTH'])
    API_TOKEN_EXPIRATION = int(config['web']['API_TOKEN_EXPIRATION'])
    OPENID_PROVIDERS = get_openid_providers()
