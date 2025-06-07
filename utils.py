from openai import OpenAI

SYSTEM_COMMAND = ("你是一个专业的财务分析师，擅长从年度账单数据中提取关键信息并生成总结.\n"
                    )
PROMPT = (
    "请根据以下年度账单数据，生成一段简洁有洞察力的年度总结，要求：\n"
    "1. 先简要概述整体收支情况。\n"
    "2. 用分点或小标题详细说明主要消费类别、月度趋势、最大/最小收支等亮点。\n"
    "3. 结尾给出理财建议。\n"
    "输出请使用Markdown格式，请严格遵守Markdown格式,开头不要输出```和markdown等多余内容\n"
    "所有标题、段落、列表项都要单独一行，且标题、段落、列表之间用空行分隔，禁止将多个标题或内容写在同一行。\n"
    "所有有序列表（如1. 2. 3.）每一项都要单独一行，并且前后用空行分隔，禁止将多个序号内容写在同一行。\n"
    "所有标题的#后面都要有空格前面都要有换行，如 \n# 一级标题 \n"
    "账单数据如下：\n"
)
class AIClient:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key,base_url="https://api.deepseek.com")

    def generate_summary_stream(self, user_id, year_report_data):
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f"{SYSTEM_COMMAND}"},
                {"role": "user", "content": f"{PROMPT}\n{year_report_data}"}
            ],
            max_tokens=2000,
            stream=True,
            
        )
        
        for chunk in response:
            if hasattr(chunk, "choices"):
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    yield delta.content