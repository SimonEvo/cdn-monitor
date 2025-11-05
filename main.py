from utils import *
from config import nodes_dict
from datetime import datetime, timedelta
from utils.feishu_sheet import FeishuSheet

if __name__ == "__main__":
    miners = ["72529", "70489"]

    webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/aed26ae1-ce7d-486b-9510-3c1f48caa038"

    pushdays = 2 #int(input()) #数值为1时为昨天数据

    target_day = (datetime.now() - timedelta(days=pushdays)).strftime('%Y%m%d')
    target_day_display = (datetime.now() - timedelta(days=pushdays)).strftime('%Y年%m月%d日')

    nodes_data = {}


    for miner in miners:
        try:
            ak = nodes_dict[miner]["ak"]
            sk = nodes_dict[miner]["sk"]
            node_ids = nodes_dict[miner]["nodes"]

            api = NiulinkAPI(ak, sk)
            debug_info = api.get_day_measure_stats(node_ids, target_day)
            # 正确解析数据
            response_data = debug_info['data']
            details = response_data.get('details', {})


            if not details:
                print("无结算数据")
                feishu_message = {
                    "msg_type": "text",
                    "content": {"text": f"{target_day_display}无结算数据"}
                }
            else:
                send_message(node_ids, webhook, details, target_day_display, miner)
                for node_id, node_info in details.items():
                    # ... [找到节点名称的逻辑] ...
                    
                    measured_amount = node_info.get('measuredAmount') or {}
                    settle_amount = measured_amount.get('settleAmount', 0)
                    
                    nodes_data[node_id] = {
                        'settle': settle_amount  # 只保存结算计量
                    }

        except Exception as e:
            print(f"执行出错: {str(e)}")

    # 在数据处理成功后
    try:
        sheet = FeishuSheet()
        
        # 先测试连接
        test_result = sheet.test_connection()
        print(f"飞书连接测试: {test_result}")
        
        # 如果连接成功，再写入数据
        if "成功" in test_result:
            sheet_result = sheet.append_data(nodes_data, target_day_display)
            print(f"飞书表格更新结果: {sheet_result}")
        
    except Exception as e:
        print(f"飞书表格操作失败: {e}")
        
    filename = "./data/mining_income.csv"
    save_to_csv(nodes_data, target_day_display, filename)