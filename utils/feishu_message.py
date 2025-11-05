import requests

def send_message(node_id, webhook, details, yesterday, miner):
    try:
        # 准备表格内容
        table_elements = []
        total_original = 0
        total_settle = 0
        
        # 遍历所有节点，构建表格行
        for node_id, node_info in details.items():
            measured_amount = node_info.get('measuredAmount', {})
            original_amount = measured_amount.get('originalAmount', 0)
            settle_amount = measured_amount.get('settleAmount', 0)
            
            # 累加总计
            total_original += original_amount
            total_settle += settle_amount
            
            # 为每个节点的数据添加一行（这里用字段模拟表格行）
            # 你可以根据需要调整显示格式，例如只显示节点ID的一部分
            short_node_id = node_id[:8] + "..."  # 缩短节点ID显示
            table_elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**节点 {node_id}**\n原始计量: {original_amount:.2f} 元\n结算计量: {settle_amount:.2f} 元"
                }
            })
        
        
        # 构建完整的飞书卡片消息
        feishu_message = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"⛏️矿主ID: {miner} {yesterday} 节点计量报告"
                    },
                    "template": "green"
                },
                "elements": [
                    # 先显示总计信息
                    {
                        "tag": "div",
                        "fields": [
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**总原始计量**\n{total_original:.2f} 元"
                                }
                            },
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md", 
                                    "content": f"**总结算计量**\n{total_settle:.2f} 元"
                                }
                            }
                        ]
                    },
                    # 添加一个分隔线
                    {
                        "tag": "hr"
                    },
                    # 这里是各个节点的详细数据表格
                    *table_elements  # 这里会展开所有表格行
                ]
            }
        }
    
        # 发送到飞书
        response = requests.post(webhook, json=feishu_message, timeout=10)
        # print(f"飞书发送结果: {response.status_code}")
        
    except Exception as e:
        print(f"执行出错: {str(e)}")