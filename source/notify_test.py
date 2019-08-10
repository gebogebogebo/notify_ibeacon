#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests

if __name__ == '__main__':
        access_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxx"
        url = "https://notify-api.line.me/api/notify"
        headers = {'Authorization': 'Bearer ' + access_token}
        message = "テスト"
        payload = {'message': message}
        requests.post(url, headers=headers, params=payload,)
 