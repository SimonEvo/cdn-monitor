import requests
from config import FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_SHEET_TOKEN, FEISHU_SHEET_ID
from datetime import datetime

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
        #print(f"测试URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            #print(f"响应状态码: {response.status_code}")
            #print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                #print("✅ 表格连接成功!")
                return "✅ 表格连接成功!"
                sheets = data.get('data', {}).get('sheets', [])
            else:
                return f"❌ 连接失败: {response.status_code}"
                
        except Exception as e:
            return f"请求异常: {e}"
    
    def get_sheet_data(self):
        """动态扩展表格：节点为行，日期为列，日期自动排序"""
        token = self.get_access_token()
        if not token:
            return "Token获取失败"
        
        headers = {'Authorization': f'Bearer {token}'}
        # 1. 读取整个表格
        read_url = f"{self.base_url}/{self.sheet_token}/values/{self.sheet_id}"
        read_response = requests.get(read_url, headers=headers)
        
        if read_response.status_code != 200:
            return f"读取表格失败: {read_response.text}"
        
        response_data = read_response.json()
        #print(f"表格内容: {response_data['data']['valueRange']['values']}")  #读取完整表格内容
        file_reader = response_data['data']['valueRange']['values']
        
        if response_data.get('code') != 0:
            print(f"API错误: {response_data.get('msg')}")
            return []
        
        return file_reader

    def build_sorted_table(self, current_data, nodes_data, new_date):
        """构建日期排序的表格"""
        
        if not current_data or len(current_data) == 0:
            # 新表格：直接创建
            header = ["节点名称", new_date]
            values = [header]
            for node_name, data in nodes_data.items():
                values.append([node_name, data['settle']])
            return values
        
        # 提取表头（第一行）
        header_row = current_data[0]  # ['节点名称', '2025年11月04日', ...]
        data_rows = current_data[1:]  # 剩下的数据行
        
        # 提取日期列并排序
        date_columns = header_row[1:]  # 跳过"节点名称"列
        
        # 添加新日期（如果不存在）
        if new_date not in date_columns:
            date_columns.append(new_date)
        
        # 日期排序（转换后排序）
        def convert_date(date_str):
            try:
                # 处理 "2025年11月04日" 格式
                if "年" in date_str and "月" in date_str and "日" in date_str:
                    return datetime.strptime(date_str, "%Y年%m月%d日")
                # 处理其他格式可以在这里添加
                else:
                    return datetime.strptime(date_str, "%Y-%m-%d")
            except:
                return datetime.min  # 无法解析的日期排在最前
        
        # 按日期对象排序，但保持字符串格式
        sorted_dates = sorted(date_columns, key=convert_date)
        
        # 构建新表头
        new_header = ["节点名称"] + sorted_dates
        
        # 重建数据行
        new_data_rows = []
        
        # 创建节点到数据的映射
        node_data_map = {}
        for row in data_rows:
            if row and len(row) > 0:
                node_name = row[0]  # 第一列是节点名称
                node_data_map[node_name] = row
        
        # 为每个节点构建新行
        all_nodes = set(node_data_map.keys()) | set(nodes_data.keys())
        
        for node_name in all_nodes:
            new_row = [node_name]  # 节点名称
            
            # 为每个日期列填充数据
            for date in sorted_dates:
                if date == new_date:
                    # 新日期的数据
                    if node_name in nodes_data:
                        new_row.append(nodes_data[node_name]['settle'])
                    else:
                        new_row.append("")  # 该节点没有新数据
                else:
                    # 查找现有数据
                    if node_name in node_data_map:
                        existing_row = node_data_map[node_name]
                        # 找到日期在原始表头中的位置
                        if date in header_row:
                            date_index = header_row.index(date)
                            if len(existing_row) > date_index:
                                new_row.append(existing_row[date_index])
                            else:
                                new_row.append("")
                        else:
                            new_row.append("")
                    else:
                        new_row.append("")  # 新节点，历史数据为空
            
            new_data_rows.append(new_row)

        
        #print(new_data_rows)
        
        return [new_header], new_data_rows
    


    def replace_table_data(self, new_header, nodes_data):
        """清空表格并填入新数据"""
        token = self.get_access_token()
        if not token:
            return "Token获取失败"
        
        headers = {'Authorization': f'Bearer {token}'}
        # 构建新表格数据
        values = new_header  # 表头
        
        values.extend(nodes_data)
    
        
        # 直接覆盖整个表格
        url = f"{self.base_url}/{self.sheet_token}/values"
        payload = {
            "valueRange": {
                "range": f"{self.sheet_id}",  # 覆盖大范围确保清空
                "values": values
            }
        }
        
        #print(f"清空并写入数据: {values}")
        response = requests.put(url, headers=headers, json=payload)
        #print(f"清空写入响应: {response.status_code}")
        return response.json()