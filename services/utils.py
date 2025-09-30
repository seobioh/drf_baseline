# gpts/utils.py
app_name = "gpts"

import json
from openai import OpenAI

from django.conf import settings

# GPT Service
class GPTService:
    def send_to_gpt_server_stream(self, system_prompt, message):
        try:            
            api_key = getattr(settings, 'OPENAI_API_KEY', None)
            if not api_key:
                yield json.dumps({
                    'content': "API 키가 설정되지 않았습니다.",
                    'is_finished': True
                })
                return
            
            client = OpenAI(api_key=api_key)
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=700,
                temperature=0.8,
                presence_penalty=0.1,
                frequency_penalty=0.1,
                stream=True
            )
            
            full_content = ""
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content_chunk = chunk.choices[0].delta.content
                    full_content += content_chunk
                    
                    # 부분 응답 전송
                    yield json.dumps({
                        'content': content_chunk,
                        'is_finished': False
                    })
            
            # 스트림 완료 신호
            yield json.dumps({
                'content': '',
                'is_finished': True
            })
            
        except Exception as e:
            yield json.dumps({
                'content': "에러가 발생했습니다",
                'is_finished': True
            })
    
    def generate_stream_response(self, system_prompt, message):
        full_content = ""
        
        for chunk_data in self.send_to_gpt_server_stream(system_prompt, message):
            chunk = json.loads(chunk_data)
            
            if not chunk.get('is_finished', False):
                yield f"data: {json.dumps(chunk)}\n\n"
                full_content += chunk.get('content', '')

            else:
                yield f"data: {json.dumps(chunk)}\n\n"
                break
        
        # 스트림 종료 신호
        yield "data: [DONE]\n\n"