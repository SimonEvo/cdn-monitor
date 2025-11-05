#!/usr/bin/env python3
import json
import requests
import hmac
import base64
import hashlib
from datetime import datetime, timedelta

class NiulinkAPI:
    def __init__(self, ak, sk):
        self.ak = ak
        self.sk = sk.encode('utf-8')
        self.host = "api.niulinkcloud.com"
    
    def get_signature(self, method, path, body=""):
        data = f"{method} {path}\nHost: {self.host}\nContent-Type: application/json\n\n{body}"
        sign = hmac.new(self.sk, data.encode('utf-8'), hashlib.sha1).digest()
        token = self.ak + ":" + base64.urlsafe_b64encode(sign).decode("utf-8")
        return "Qiniu " + token
    
    def get_day_measure_stats(self, node_ids, day):
        path = f"/v1/nodes/batch/amount/details"
        
        # POST请求的body数据
        body_data = {
            "nodeIds": node_ids,  # 节点ID列表
            "day": day
        }
        
        # 签名数据需要包含body内容
        body_str = json.dumps(body_data)
        
        headers = {
            'Authorization': self.get_signature("POST", path, body_str),
            'Content-Type': 'application/json'
        }
        url = f"https://{self.host}{path}"
        
        print(f"请求URL: {url}")
        print(f"请求Body: {body_str}")
        
        response = requests.post(url, headers=headers, data=body_str)
        print(f"原始响应: {response.text}")
        
        return {
            'data': response.json(),
            'url': url,
            'response': response.text
        }