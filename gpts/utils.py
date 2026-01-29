# gpts/utils.py
app_name = "gpts"

import json

from openai import OpenAI

from django.conf import settings

from .models import GPTPrompt, GPTChatMessage

class GPTService:
    SUMMARY_TRIGGER_TOKENS = 3000
    SUMMARY_TARGET_TOKENS = 800
    STREAM_SAVE_EVERY = 20

    def __init__(self, chat_room):
        self.chat_room = chat_room
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def _maybe_update_summary(self):
        last = self.chat_room.last_summarized_message

        qs = self.chat_room.messages.filter(role__in=["user", "assistant"])
        if last:
            qs = qs.filter(id__gt=last.id)

        messages = list(qs.order_by("id"))
        if not messages:
            return

        total_tokens = sum(m.token_count for m in messages)

        if total_tokens < self.SUMMARY_TRIGGER_TOKENS:
            return

        summary_text = self._summarize(messages)

        self.chat_room.summary = summary_text
        self.chat_room.summary_token_count = len(summary_text) // 4
        self.chat_room.last_summarized_message = messages[-1]
        self.chat_room.save(update_fields=["summary", "summary_token_count", "last_summarized_message"])

    def _summarize(self, messages):
        text = "\n".join(
            f"{m.role}: {m.message}"
            for m in messages
        )

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"Summarize the following conversation in under {self.SUMMARY_TARGET_TOKENS} tokens."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.3,
        )

        return response.choices[0].message.content

    def _generate_room_title(self, user_message, assistant_text):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Create a short chat title under 20 characters."
                    },
                    {
                        "role": "user",
                        "content": f"User: {user_message.message}\nAssistant: {assistant_text}"
                    }
                ],
                temperature=0.3,
            )

            title = response.choices[0].message.content.strip()
            return title[:30]

        except Exception:
            return "새 채팅방"

    def _build_context(self):
        context = []

        if self.chat_room.prompt:
            context.append({"role": "system", "content": self.chat_room.prompt.prompt})

        if self.chat_room.summary:
            context.append({"role": "system", "content": f"Conversation summary:\n{self.chat_room.summary}"})

        qs = self.chat_room.messages.all()
        if self.chat_room.last_summarized_message_id:
            qs = qs.filter(id__gt=self.chat_room.last_summarized_message_id)

        for m in qs.order_by("id"):
            context.append({"role": m.role, "content": m.message})

        return context

    def handle(self, user_message: GPTChatMessage) -> GPTChatMessage:
        self._maybe_update_summary()
        messages = self._build_context()
        response = self.client.chat.completions.create(model=user_message.model, messages=messages, temperature=0.7)
        assistant_text = response.choices[0].message.content
        return GPTChatMessage.objects.create(chat_room=self.chat_room,role="assistant",model=user_message.model,message=assistant_text)

    def stream(self, user_message: GPTChatMessage):
        assistant_message = GPTChatMessage.objects.create(chat_room=self.chat_room, role="assistant", model=user_message.model, message="")

        try:
            self._maybe_update_summary()
            messages = self._build_context()
            stream = self.client.chat.completions.create(model=user_message.model, messages=messages, temperature=0.7, stream=True)

            full_text = ""
            counter = 0
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if not delta:
                    continue

                full_text += delta
                counter += 1

                if counter % self.STREAM_SAVE_EVERY == 0:
                    assistant_message.message = full_text
                    assistant_message.save(update_fields=["message"])

                yield f"data: {delta}\n\n"

            assistant_message.message = full_text
            assistant_message.token_count = len(full_text) // 4
            assistant_message.save(update_fields=["message", "token_count"])
            yield f"event: done\ndata: {assistant_message.id}\n\n"

        except Exception as e:
            assistant_message.is_error = True
            assistant_message.message = str(e)
            assistant_message.save(update_fields=["is_error", "message"])
            yield f"event: error\ndata: {str(e)}\n\n"

    def stream_with_init(self, user_message: GPTChatMessage):
        yield f"event: init\ndata: {json.dumps({'room_id': self.chat_room.id})}\n\n"
        assistant_message = GPTChatMessage.objects.create(chat_room=self.chat_room, role="assistant", model=user_message.model, message="")

        try:
            self._maybe_update_summary()
            messages = self._build_context()
            stream = self.client.chat.completions.create(model=user_message.model, messages=messages, temperature=0.7, stream=True)

            full_text = ""
            counter = 0
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if not delta:
                    continue

                full_text += delta
                counter += 1

                if counter % self.STREAM_SAVE_EVERY == 0:
                    assistant_message.message = full_text
                    assistant_message.save(update_fields=["message"])

                yield f"data: {delta}\n\n"

            assistant_message.message = full_text
            assistant_message.token_count = len(full_text) // 4
            assistant_message.save(update_fields=["message", "token_count"])

            # 채팅방 이름 생성
            title = self._generate_room_title(user_message, full_text)
            self.chat_room.name = title
            self.chat_room.save(update_fields=["name"])
            yield f"event: meta\ndata: {json.dumps({'room_id': self.chat_room.id, 'room_name': title, 'prompt_id': self.chat_room.prompt.id if self.chat_room.prompt else None, 'prompt_name': self.chat_room.prompt.name if self.chat_room.prompt else None})}\n\n"

            yield f"event: done\ndata: {json.dumps({'assistant_id': assistant_message.id})}\n\n"

        except Exception as e:
            assistant_message.is_error = True
            assistant_message.message = str(e)
            assistant_message.save(update_fields=["is_error", "message"])
            yield f"event: error\ndata: {str(e)}\n\n"


class GPTSessionService:
    def __init__(self, model="gpt-4o-mini", prompt: GPTPrompt = None):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model
        self.prompt = prompt

    def ask(self, message: str) -> str:
        messages = []
        if self.prompt:
            messages.append({"role": "system", "content": self.prompt.prompt})
        messages.append({"role": "user", "content": message})
        response = self.client.chat.completions.create(model=self.model, messages=messages, temperature=0.7,)
        return response.choices[0].message.content

    def stream(self, message: str):
        messages = []
        if self.prompt:
            messages.append({"role": "system", "content": self.prompt.prompt})
        messages.append({"role": "user", "content": message})
        stream = self.client.chat.completions.create(model=self.model, messages=messages, temperature=0.7, stream=True)

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield f"data: {delta}\n\n"

        yield "event: done\ndata: end\n\n"
