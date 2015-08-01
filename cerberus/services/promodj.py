# encoding: utf-8

import os

import requests

from .interface import BaseService

class PromoDJ(BaseService):
    def __init__(self, config):
        self.config = config
        self.req = requests.Session()
        
    def login(self):
        payload = { self.config['form']['login']: self.config['login'], self.config['form']['password']: self.config['password'] }
        url = self.config['form']['url']
        r = self.req.post(url, data=payload)
        return self.req.cookies.get_dict()

    def upload(self, filename="", title="", description="" ,category="", keywords=[]):
        
        return {}

    def delete(self, video_id):
	return 0
