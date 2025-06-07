from openai import OpenAI

SYSTEM_COMMAND = "你是一个专业的财务分析师，擅长从年度账单数据中提取关键信息并生成总结。"
PROMPT = (
    "请根据以下年度账单数据，生成一段简洁有洞察力的年度总结，要求：\n"
    "1. 先简要概述整体收支情况。\n"
    "2. 用分点或小标题详细说明主要消费类别、月度趋势、最大/最小收支等亮点。\n"
    "3. 结尾给出理财建议。\n"
    "4. 输出请使用Markdown格式，适当使用列表、粗体、小标题等增强可读性。\n"
    "请严格遵守Markdown格式，标题前后要有空行（如 ## 标题 前后要空一行),列表项要单独一行，且前面要有 -  或 * ,换行要用两个空格加回车，或直接空一行\n"
    "账单数据如下："
)
class AIClient:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key,base_url="https://openrouter.ai/api/v1")

    def generate_summary_stream(self, user_id, year_report_data):
        response = self.client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {"role": "system", "content": f"{SYSTEM_COMMAND}"},
                {"role": "user", "content": f"{PROMPT}\n{year_report_data}"}
            ],
            max_tokens=1000.,
            stream=True
        )
        
        for chunk in response:
            if hasattr(chunk, "choices"):
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    print(delta.content, end='', flush=True)
                    yield delta.content