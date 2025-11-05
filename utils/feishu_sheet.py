import requests
from config import FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_SHEET_TOKEN, FEISHU_SHEET_ID


class FeishuSheet:
    def __init__(self):
        self.app_id = FEISHU_APP_ID
        self.app_secret = FEISHU_APP_SECRET
        self.sheet_token = FEISHU_SHEET_TOKEN
        self.sheet_id = FEISHU_SHEET_ID
        self.base_url = "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets"
        
    def get_access_token(self):
        """获取飞书访问令牌"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        response = requests.post(url, json=payload)
        return response.json().get('tenant_access_token')
    
    def test_connection(self):
        """测试连接 - 使用获取表格元数据API"""
        token = self.get_access_token()
        if not token:
            return "Token获取失败"
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # 使用正确的API：获取表格元数据
        url = f"{self.base_url}/{self.sheet_token}/metainfo"
        print(f"测试URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 表格连接成功!")
                sheets = data.get('data', {}).get('sheets', [])
                for sheet in sheets:
                    print(f"工作表: {sheet.get('title')} (ID: {sheet.get('sheetId')})")
                return "连接成功"
            else:
                return f"❌ 连接失败: {response.status_code}"
                
        except Exception as e:
            return f"请求异常: {e}"
    
    def append_data(self, nodes_data, date):
        """使用追加数据API写入数据"""
        token = self.get_access_token()
        if not token:
            return "Token获取失败"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json; charset=utf-8'
        }
        
        # 1. 先获取工作表信息
        meta_url = f"{self.base_url}/{self.sheet_token}/metainfo"
        meta_response = requests.get(meta_url, headers=headers)
        
        if meta_response.status_code != 200:
            return f"获取工作表信息失败: {meta_response.text}"
        
        meta_data = meta_response.json()
        sheets = meta_data.get('data', {}).get('sheets', [])
        
        if not sheets:
            return "未找到工作表"
        
        # 使用第一个工作表的ID
        sheet_id = sheets[0].get('sheetId')
        sheet_title = sheets[0].get('title')
        print(f"使用工作表: {sheet_title} (ID: {sheet_id})")
        
        # 2. 构建要写入的数据
        values = self.prepare_values(nodes_data, date)
        
        # 3. 使用工作表ID而不是名称
        url = f"{self.base_url}/{self.sheet_token}/values_append"
        payload = {
            "valueRange": {
                "range": sheet_id,  # 使用工作表ID
                "values": values
            }
        }
        
        print(f"追加数据URL: {url}")
        print(f"追加数据Payload: {payload}")
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            print(f"数据写入响应: {response.status_code}")
            print(f"数据写入内容: {response.text}")
            return response.json()
        except Exception as e:
            return f"数据写入失败: {e}"
    
    def prepare_values(self, nodes_data, date):
        """准备要写入的数据"""
        # 简化版：直接构建新表格
        values = [
            ["节点名称", date],  # 表头
        ]
        
        for node_name, data in nodes_data.items():
            values.append([node_name, data['settle']])
            
        return values