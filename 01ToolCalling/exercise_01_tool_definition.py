"""
============================================================
练习 1（入门）：设计工具定义
============================================================

【题目描述】
为一个"个人财务助手" Agent 设计 3 个工具的定义。
该助手帮助用户管理银行账户，需要具备以下能力：
  1. 查询账户余额 — 用户想知道某个账户里还有多少钱
  2. 转账 — 用户想从一个账户转钱到另一个账户
  3. 查询交易记录 — 用户想看某个账户最近的交易记录

【要求】
- 只写工具定义（Python 字典 / JSON Schema 格式），不写工具的实现逻辑
- 每个工具必须包含：name、description、parameters
- description 要足够清晰，让 LLM 知道什么时候该用、什么时候不该用
- parameters 中每个参数要有：type、description，区分 required / optional
- 参数类型正确（数值用 number、枚举用 enum 等）
- 考虑实际场景中的合理约束（如金额必须大于 0）

【思考提示】
- 查询余额需要什么参数？用账户 ID 还是账户类型？
- 转账需要哪些必填参数？金额应该用什么类型？需要什么约束？
- 交易记录是否需要分页？时间范围过滤？
- description 中是否要说明返回值的格式？

【学习目的】
- 理解工具定义的三要素（name / description / parameters）
- 练习写出高质量的工具描述，这是影响 LLM 工具选择准确率的最关键因素
- 掌握 JSON Schema 的基本用法（type / description / enum / required）
============================================================
"""

# ==================== 工具 1：查询账户余额 ====================
get_account_balance = {
    "name": "get_account_balance",
    "description": "当需要查询某个账户余额时使用。不能用于查询交易记录。返回 JSON，包含 balance（可用余额，单位元）",  # TODO: 填写工具描述
    "parameters": {
        "type": "object",
        "properties": {
            # TODO: 定义参数
            "account_id": {
                "type": "string",
                "description": "账户ID"
            }
        },
        "required": ["account_id"],  # TODO: 填写必填参数列表
    },
}

# ==================== 工具 2：转账 ====================
transfer_money = {
    "name": "transfer_money",
    "description": "当需要从一个账户转账到另一个账户时使用。转账操作不可逆，需要用户确认。返回 JSON，包含 success（是否成功）。",  # TODO: 填写工具描述
    "parameters": {
        "type": "object",
        "properties": {
            # TODO: 定义参数
            "from_account_id": {
                "type": "string",
                "description": "转出账户ID"
            },
            "to_account_id": {
                "type": "string",
                "description": "转入账户ID"
            },
            "amount": {
                "type": "number",
                "description": "转账金额，单位元。最小为0.01,最大为100000000。",
                "minimum": 0.01,
                "maximum": 100000000,
            },
        },
        "required": ["from_account_id", "to_account_id", "amount"],  # TODO: 填写必填参数列表
    },
}

# ==================== 工具 3：查询交易记录 ====================
get_transactions = {
    "name": "get_transactions",
    "description": "当需要查询某个账户最近的交易记录时使用。不能用于查询余额。返回JSON，包含 transactions（交易记录列表）。",  # TODO: 填写工具描述
    "parameters": {
        "type": "object",
        "properties": {
            # TODO: 定义参数
            "account_id": {
                "type": "string",
                "description": "账户ID"
            },
            "start_date": {
                "type": "string",
                "description": "开始日期。格式为YYYY-MM-DD。最小为1990-01-01。默认为当前日期前30天",
            },
            "end_date": {
                "type": "string",
                "description": "结束日期。格式为YYYY-MM-DD。最小为1990-01-01。默认为当前日期。必须大于开始日期。"
            },
            "page_size": {
                "type": "integer",
                "description": "每页交易记录数量。默认为10，最小为1，最大为100。",
                "default": 10,
                "minimum": 1,
                "maximum": 100,
            },
            "page_number": {
                "type": "integer",
                "description": "页码。默认为1，最小为1。",
                "default": 1,
                "minimum": 1,
            }
        },
        "required": ["account_id"],  # TODO: 填写必填参数列表
    },
}


# ==================== 验证区（不需要修改） ====================
if __name__ == "__main__":
    import json

    tools = [get_account_balance, transfer_money, get_transactions]

    for tool in tools:
        print(f"\n{'=' * 50}")
        print(f"工具名称: {tool['name']}")
        print(f"描述: {tool['description']}")
        print(f"参数定义:")
        print(json.dumps(tool["parameters"], indent=2, ensure_ascii=False))

        assert tool["description"], f"❌ {tool['name']} 缺少 description"
        assert tool["parameters"]["properties"], f"❌ {tool['name']} 缺少参数定义"
        assert tool["parameters"]["required"], f"❌ {tool['name']} 缺少 required 字段"

    print(f"\n{'=' * 50}")
    print("✅ 基础校验通过！请提交给教练评审。")
