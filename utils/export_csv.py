import csv
import os
from datetime import datetime

def save_to_csv(nodes_data, date, filename):
    """
    保存节点数据到CSV文件
    格式：节点名 | 日期1 | 日期2 | 日期3 ...
    """
    #filename = "/root/cdn-monitor/data/mining_income.csv"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # 读取现有数据
    existing_data = {}
    existing_dates = set()
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                node_name = row['节点名称']
                existing_data[node_name] = row
                existing_dates.update(row.keys())
    except FileNotFoundError:
        pass
    
    # 更新数据
    for node_name, data in nodes_data.items():
        if node_name not in existing_data:
            existing_data[node_name] = {'节点名称': node_name}
        existing_data[node_name][date] = data['settle']  # 只保存结算计量
    
    # 构建所有日期列（按日期排序）
    all_dates = sorted(existing_dates - {'节点名称'})
    all_dates.append(date) if date not in all_dates else None
    all_dates.sort()
    
    fieldnames = ['节点名称'] + all_dates
    
    # 写入CSV
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for node_data in existing_data.values():
            writer.writerow(node_data)
    
    print(f"数据已更新: {filename}")