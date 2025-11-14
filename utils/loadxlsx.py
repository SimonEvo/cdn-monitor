import pandas as pd
import json

class dailysheet:
    """
    需要在公司节点管理网站下载当天的“账单管理”报告然后运行
    """
    def __init__(self, filepath):

        df = pd.read_excel(filepath)
        data_dict = df.to_dict('records')

        self.dict = data_dict
        

    def save_to_json(self, key):
        try:
            with open('data.json', 'r', encoding='utf-8') as f:
                loc_dict = json.load(f)
        except:
            loc_dict = {}

        if(key in loc_dict):
            nodeIDs = loc_dict[key]['节点ID']
        else:
            nodeIDs = []
            loc_dict[key] = {'节点ID': nodeIDs}
        
        
        for x in self.dict:
            
            if(str(x['供应商ID']).split('.')[0] == key):
                if x['节点ID'] not in nodeIDs:
                    nodeIDs.append(x['节点ID'])
        
        loc_dict[key]['节点ID'] = nodeIDs

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(loc_dict, f, ensure_ascii=False, indent=4)

        
    def compare(self):
        with open('data.json', 'r', encoding='utf-8') as f:
            loc_dict = json.load(f)
        
        miner_gone = []
        nodes_gone = []

        key_list = list(loc_dict.keys())
        key_list_today = []
        for item in self.dict:
            formed = str(item['供应商ID']).split('.')[0]
            if(formed not in key_list_today):
                key_list_today.append(formed)

        for k in key_list:
            if k not in key_list_today:
                miner_gone.append(k)
                del loc_dict[k]

        print(f"这些渠道的收益今天完全没有记录：{miner_gone}")
        print(key_list_today)
        for item in self.dict:
            formed = str(item['供应商ID']).split('.')[0]
            if not pd.isna(item['节点ID']) and formed in key_list_today:
                print(item['节点ID'])
                loc_dict[formed]['节点ID'].remove(item['节点ID'])
        
        for supplier_id, data in loc_dict.items():
            print(f"{supplier_id}: {len(data['节点ID'])}个节点")
        