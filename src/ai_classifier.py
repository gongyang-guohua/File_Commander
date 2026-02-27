import os
import google.generativeai as genai
from openai import OpenAI
from typing import List, Dict, Optional
from dotenv import load_dotenv
import json
import logging

# 强制加载环境变量，确保获取最新的 API Key
load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)

class AIClassifier:
    def __init__(self):
        self.providers = []
        
        # 1. Kimi (Moonshot)
        if os.getenv("MOONSHOT_API_KEY"):
            self.providers.append({
                "name": "kimi",
                "client": OpenAI(
                    api_key=os.getenv("MOONSHOT_API_KEY"),
                    base_url="https://api.moonshot.cn/v1",
                ),
                "model": "moonshot-v1-8k"
            })

        # 2. OpenAI
        if os.getenv("OPENAI_API_KEY"):
            key = os.getenv("OPENAI_API_KEY")
            print(f"DEBUG: OpenAI Key loaded: {key[:10]}...{key[-5:]}")
            self.providers.append({
                "name": "openai",
                "client": OpenAI(api_key=key),
                "model": "gpt-4o"
            })

        # 3. Gemini
        if os.getenv("GOOGLE_API_KEY"):
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.providers.append({
                "name": "gemini",
                "client": genai.GenerativeModel("models/gemini-2.5-flash"),
                "model": "models/gemini-2.5-flash"
            })
            
        if not self.providers:
            print("Warning: No AI API Key found.")

    def _call_provider(self, provider, prompt, json_mode=False):
        try:
            print(f"Trying provider: {provider['name']}...")
            if provider['name'] in ["kimi", "openai"]:
                response = provider['client'].chat.completions.create(
                    model=provider['model'],
                    messages=[
                        {"role": "system", "content": "你是一个文件分类引擎。请直接输出结果，不要包含 markdown 格式标记。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"} if json_mode and provider['name'] == "openai" else None
                )
                return response.choices[0].message.content
            
            elif provider['name'] == "gemini":
                response = provider['client'].generate_content(prompt)
                return response.text
                
        except Exception as e:
            print(f"Provider {provider['name']} failed: {e}")
            return None

    def suggest_structure(self, file_list: List[str]) -> str:
        prompt = f"""
        我有一组杂乱的文件，请帮我整理并按“项目”进行分类。
        请仔细分析文件名和路径，推测它们可能属于什么项目。
        
        文件列表样本 (前50个):
        {json.dumps(file_list[:50], ensure_ascii=False, indent=2)}
        
        请输出一个建议的文件夹结构，并为每个主要项目提供简短描述。
        请使用中文回答。
        """
        
        for p in self.providers:
            result = self._call_provider(p, prompt)
            if result:
                return result
        return "所有 AI 模型调用均失败。"

    def batch_classify(self, files_metadata: List[Dict]) -> str:
        simple_list = [f"{f['path']}" for f in files_metadata]
        
        prompt = f"""
        请分析以下文件路径，并将它们归类到合适的“项目”中。
        如果文件看起来是通用的（如安装包、临时文件、系统文件），请归类为 "General" 或 "Trash"。
        如果能识别出具体的项目名称（如 "Project A", "Website v1"），请使用具体的项目名。
        
        请直接输出 JSON 数组，不要包含 Markdown 格式标记（如 ```json）。
        
        输出格式示例:
        [
            {{"path": "D:\\Work\\A.doc", "project": "WorkDocs", "reason": "文档所在的文件夹"}},
            {{"path": "D:\\Tmp\\B.tmp", "project": "Trash", "reason": "临时文件"}}
        ]
        
        文件列表:
        {json.dumps(simple_list, ensure_ascii=False, indent=2)}
        """
        
        for p in self.providers:
            # Kimi 不支持 response_format="json_object"，所以仅 OpenAI 开启
            json_mode = (p['name'] == "openai")
            result = self._call_provider(p, prompt, json_mode=json_mode)
            if result:
                return result
                
        return "[]"

if __name__ == "__main__":
    classifier = AIClassifier()
    sample_files = [
        "J:\\Work\\ProjectA\\design.psd",
        "J:\\Downloads\\budget_2024.xlsx",
    ]
    print(classifier.suggest_structure(sample_files))
