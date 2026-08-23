# gpts/utils.py
app_name = "gpts"

import json
import math

from openai import OpenAI

from django.conf import settings

from .models import GPTPrompt, GPTChatMessage, GPTEmbeddingCategory, GPTEmbedding

# Similarity Engine
# <-------------------------------------------------------------------------------------------------------------------------------->
class SimilarityEngine:
    ALGORITHMS = ["cosine", "dot_product", "euclidean", "manhattan"]

    @staticmethod
    def cosine(v1, v2):
        dot = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)

    @staticmethod
    def dot_product(v1, v2):
        return sum(a * b for a, b in zip(v1, v2))

    @staticmethod
    def euclidean(v1, v2):
        dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))
        return 1.0 / (1.0 + dist)

    @staticmethod
    def manhattan(v1, v2):
        dist = sum(abs(a - b) for a, b in zip(v1, v2))
        return 1.0 / (1.0 + dist)

    @classmethod
    def calculate(cls, v1, v2, algorithm="cosine"):
        algo = algorithm.lower().strip()
        if algo == "cosine":
            return cls.cosine(v1, v2)
        elif algo in ("dot_product", "dot"):
            return cls.dot_product(v1, v2)
        elif algo in ("euclidean", "l2"):
            return cls.euclidean(v1, v2)
        elif algo in ("manhattan", "l1"):
            return cls.manhattan(v1, v2)
        else:
            raise ValueError(f"Unsupported algorithm: '{algorithm}'. Supported: {', '.join(cls.ALGORITHMS)}")


# GPT Embedding Service
# <-------------------------------------------------------------------------------------------------------------------------------->
class GPTEmbeddingService:
    DEFAULT_MODEL = "text-embedding-3-small"

    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key or settings.OPENAI_API_KEY)

    def get_embedding(self, text, model=DEFAULT_MODEL):
        response = self.client.embeddings.create(input=text, model=model)
        return response.data[0].embedding

    def get_embeddings(self, texts, model=DEFAULT_MODEL):
        if not texts:
            return []
        response = self.client.embeddings.create(input=texts, model=model)
        return [item.embedding for item in response.data]

    def route_categories(self, query: str, prompt: GPTPrompt = None, history: str = None) -> list[str]:
        try:
            qs = GPTEmbeddingCategory.objects.filter(is_active=True)
            if prompt:
                prompt_categories = qs.filter(prompt=prompt)
                if prompt_categories.exists():
                    qs = prompt_categories

            categories = list(qs)
            if not categories:
                return []

            cat_names = {c.name.lower(): c.name for c in categories}
            cat_lines = "\n".join(f"- {c.name}: {c.description or c.name}" for c in categories)

            system_prompt = (
                "You are an intent and multi-category classifier for a knowledge retrieval system.\n"
                "Given the available knowledge categories and conversation context below, select ALL categories that are relevant to the user's query.\n"
                "Important Rules:\n"
                "1. If the query touches upon multiple topics, domains, or entities (e.g. asking about car models/features AND payment/refunds AND points/coupons), include ALL relevant categories in the array.\n"
                "2. Check entities, keywords, and user intents carefully against each category description.\n"
                "3. If the query is casual chat, small talk, general conversation, or general facts/coding that do not require knowledge from any domain category, respond with [].\n"
                "4. Respond ONLY with a valid JSON array of category names (e.g. [\"car_manual\", \"cs_faq\"]) without markdown formatting, backticks, or explanations.\n\n"
                f"Categories:\n{cat_lines}"
            )

            messages = [{"role": "system", "content": system_prompt}]
            if history:
                messages.append({"role": "system", "content": f"Conversation History:\n{history}"})
            messages.append({"role": "user", "content": query})

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.0,
                max_tokens=50
            )

            raw_content = response.choices[0].message.content.strip()
            if raw_content.startswith("```"):
                raw_content = raw_content.strip("`").removeprefix("json").strip()

            try:
                parsed = json.loads(raw_content)
                if isinstance(parsed, list):
                    matched = [cat_names[str(item).lower()] for item in parsed if str(item).lower() in cat_names]
                    return matched
                elif isinstance(parsed, str) and parsed.lower() in cat_names:
                    return [cat_names[parsed.lower()]]

            except Exception:
                # Fallback text matching
                raw_lower = raw_content.lower()
                matched = [name for key, name in cat_names.items() if key in raw_lower]
                return matched

            return []

        except Exception:
            return []

    def find_similar(self, query: str, prompt: GPTPrompt = None, categories: list = None, algorithm: str = "cosine", top_k: int = 3, embedding_model: str = None, history: str = None):
        model_to_use = embedding_model

        target_cats = []
        if categories:
            if isinstance(categories, str):
                target_cats = [c.strip() for c in categories.split(",") if c.strip()]
            elif isinstance(categories, (list, tuple, set)):
                target_cats = [str(c).strip() for c in categories if c]

        if target_cats:
            cat_objs = GPTEmbeddingCategory.objects.filter(name__in=target_cats, is_active=True)
            if not cat_objs.exists():
                return []
            if not model_to_use:
                model_to_use = cat_objs.first().embedding_model
            qs = GPTEmbedding.objects.filter(category__in=cat_objs, is_active=True).exclude(embedding__isnull=True)

        elif prompt:
            prompt_categories = GPTEmbeddingCategory.objects.filter(prompt=prompt, is_active=True)
            if prompt_categories.exists():
                cat_ids = prompt_categories.values_list('id', flat=True)
                if not model_to_use:
                    model_to_use = prompt_categories.first().embedding_model
                qs = GPTEmbedding.objects.filter(category_id__in=cat_ids, is_active=True).exclude(embedding__isnull=True)
            else:
                if not model_to_use:
                    model_to_use = self.DEFAULT_MODEL
                qs = GPTEmbedding.objects.filter(is_active=True).exclude(embedding__isnull=True)

        else:
            if not model_to_use:
                model_to_use = self.DEFAULT_MODEL
            qs = GPTEmbedding.objects.filter(is_active=True).exclude(embedding__isnull=True)

        embeddings_list = list(qs.select_related('category'))
        if not embeddings_list:
            return []

        search_query = f"{history}\n{query}" if history else query
        query_vec = self.get_embedding(search_query, model=model_to_use or self.DEFAULT_MODEL)

        results = []
        for item in embeddings_list:
            score = SimilarityEngine.calculate(query_vec, item.embedding, algorithm=algorithm)
            results.append({
                "id": item.id,
                "title": item.title,
                "content": item.content,
                "category": item.category.name,
                "score": round(score, 6),
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]


# GPT Service (Chat Room)
# <-------------------------------------------------------------------------------------------------------------------------------->
class GPTService:
    SUMMARY_TRIGGER_TOKENS = 3000
    SUMMARY_TARGET_TOKENS = 800
    STREAM_SAVE_EVERY = 20

    def __init__(self, chat_room):
        self.chat_room = chat_room
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_service = GPTEmbeddingService()

    def _get_history_text(self):
        parts = []
        if self.chat_room.summary:
            parts.append(f"Summary: {self.chat_room.summary}")

        qs = self.chat_room.messages.filter(role__in=["user", "assistant"])
        if self.chat_room.last_summarized_message_id:
            qs = qs.filter(id__gt=self.chat_room.last_summarized_message_id)

        for m in qs.order_by("id"):
            parts.append(f"{m.role}: {m.message}")

        return "\n".join(parts)

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
        text = "\n".join(f"{m.role}: {m.message}" for m in messages)
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

    def _build_context(self, extra_context=None):
        context = []

        if self.chat_room.prompt:
            context.append({"role": "system", "content": self.chat_room.prompt.prompt})

        if extra_context:
            context.append({"role": "system", "content": f"Reference Context:\n{extra_context}"})

        if self.chat_room.summary:
            context.append({"role": "system", "content": f"Conversation summary:\n{self.chat_room.summary}"})

        qs = self.chat_room.messages.all()
        if self.chat_room.last_summarized_message_id:
            qs = qs.filter(id__gt=self.chat_room.last_summarized_message_id)

        for m in qs.order_by("id"):
            context.append({"role": m.role, "content": m.message})

        return context

    def _retrieve_context(self, message: str, use_embedding=True, embedding_algorithm="cosine", categories=None, top_k=3):
        if not use_embedding:
            return None, [], {"is_routed": False, "categories": [], "use_embedding": False}

        history_text = self._get_history_text()
        was_auto_routed = False

        target_categories = []
        if categories:
            if isinstance(categories, str):
                target_categories = [c.strip() for c in categories.split(",") if c.strip()]
            elif isinstance(categories, (list, tuple, set)):
                target_categories = [str(c).strip() for c in categories if c]

        if not target_categories:
            was_auto_routed = True
            target_categories = self.embedding_service.route_categories(query=message, prompt=self.chat_room.prompt, history=history_text)

        routing_info = {
            "is_routed": bool(target_categories),
            "categories": target_categories,
            "was_auto_routed": was_auto_routed
        }

        if not target_categories:
            return None, [], routing_info

        relevant = self.embedding_service.find_similar(
            query=message,
            prompt=self.chat_room.prompt,
            categories=target_categories,
            algorithm=embedding_algorithm,
            top_k=top_k,
            history=history_text
        )

        if relevant:
            context_str = "\n\n".join(f"[{i+1}] ({item.get('category') or ''}) {item.get('title') or ''}\n{item['content']}".strip() for i, item in enumerate(relevant))
            return context_str, relevant, routing_info

        return None, [], routing_info

    def handle(self, user_message: GPTChatMessage, use_embedding=True, embedding_algorithm="cosine", categories=None, top_k=3) -> GPTChatMessage:
        self._maybe_update_summary()
        extra_context, _, _ = self._retrieve_context(message=user_message.message, use_embedding=use_embedding, embedding_algorithm=embedding_algorithm, categories=categories, top_k=top_k)
        messages = self._build_context(extra_context=extra_context)
        response = self.client.chat.completions.create(model=user_message.model, messages=messages, temperature=0.7)
        assistant_text = response.choices[0].message.content
        return GPTChatMessage.objects.create(chat_room=self.chat_room, role="assistant", model=user_message.model, message=assistant_text)

    def stream(self, user_message: GPTChatMessage, use_embedding=True, embedding_algorithm="cosine", categories=None, top_k=3):
        assistant_message = GPTChatMessage.objects.create(chat_room=self.chat_room, role="assistant", model=user_message.model, message="")

        try:
            extra_context, relevant, routing_info = self._retrieve_context(message=user_message.message, use_embedding=use_embedding, embedding_algorithm=embedding_algorithm, categories=categories, top_k=top_k)
            if use_embedding:
                yield f"event: routing\ndata: {json.dumps(routing_info, ensure_ascii=False)}\n\n"

            if relevant:
                yield f"event: context\ndata: {json.dumps({'categories': routing_info.get('categories', []), 'relevant_contexts': relevant, 'algorithm': embedding_algorithm}, ensure_ascii=False)}\n\n"

            self._maybe_update_summary()
            messages = self._build_context(extra_context=extra_context)
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

    def stream_with_init(self, user_message: GPTChatMessage, use_embedding=True, embedding_algorithm="cosine", categories=None, top_k=3):
        yield f"event: init\ndata: {json.dumps({'room_id': self.chat_room.id})}\n\n"
        assistant_message = GPTChatMessage.objects.create(chat_room=self.chat_room, role="assistant", model=user_message.model, message="")

        try:
            extra_context, relevant, routing_info = self._retrieve_context(message=user_message.message, use_embedding=use_embedding, embedding_algorithm=embedding_algorithm, categories=categories, top_k=top_k)
            if use_embedding:
                yield f"event: routing\ndata: {json.dumps(routing_info, ensure_ascii=False)}\n\n"

            if relevant:
                yield f"event: context\ndata: {json.dumps({'categories': routing_info.get('categories', []), 'relevant_contexts': relevant, 'algorithm': embedding_algorithm}, ensure_ascii=False)}\n\n"

            self._maybe_update_summary()
            messages = self._build_context(extra_context=extra_context)
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


# GPT Session Service
# <-------------------------------------------------------------------------------------------------------------------------------->
class GPTSessionService:
    def __init__(self, model="gpt-4o-mini", prompt: GPTPrompt = None):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model
        self.prompt = prompt
        self.embedding_service = GPTEmbeddingService()

    def _retrieve_context(self, message: str, use_embedding=True, embedding_algorithm="cosine", categories=None, top_k=3):
        if not use_embedding:
            return None, [], {"is_routed": False, "categories": [], "use_embedding": False}

        was_auto_routed = False

        target_categories = []
        if categories:
            if isinstance(categories, str):
                target_categories = [c.strip() for c in categories.split(",") if c.strip()]
            elif isinstance(categories, (list, tuple, set)):
                target_categories = [str(c).strip() for c in categories if c]

        if not target_categories:
            was_auto_routed = True
            target_categories = self.embedding_service.route_categories(query=message, prompt=self.prompt)

        routing_info = {
            "is_routed": bool(target_categories),
            "categories": target_categories,
            "was_auto_routed": was_auto_routed
        }

        if not target_categories:
            return None, [], routing_info

        relevant = self.embedding_service.find_similar(
            query=message,
            prompt=self.prompt,
            categories=target_categories,
            algorithm=embedding_algorithm,
            top_k=top_k
        )

        if relevant:
            context_str = "\n\n".join(f"[{i+1}] ({item.get('category') or ''}) {item.get('title') or ''}\n{item['content']}".strip() for i, item in enumerate(relevant))
            return context_str, relevant, routing_info

        return None, [], routing_info

    def ask(self, message: str, use_embedding=True, embedding_algorithm="cosine", categories=None, top_k=3) -> str:
        messages = []
        if self.prompt:
            messages.append({"role": "system", "content": self.prompt.prompt})

        extra_context, _, _ = self._retrieve_context(message=message, use_embedding=use_embedding, embedding_algorithm=embedding_algorithm, categories=categories, top_k=top_k)
        if extra_context:
            messages.append({"role": "system", "content": f"Reference Context:\n{extra_context}"})

        messages.append({"role": "user", "content": message})
        response = self.client.chat.completions.create(model=self.model, messages=messages, temperature=0.7)
        return response.choices[0].message.content

    def stream(self, message: str, use_embedding=True, embedding_algorithm="cosine", categories=None, top_k=3):
        messages = []
        if self.prompt:
            messages.append({"role": "system", "content": self.prompt.prompt})

        extra_context, relevant, routing_info = self._retrieve_context(message=message, use_embedding=use_embedding, embedding_algorithm=embedding_algorithm, categories=categories, top_k=top_k)
        if use_embedding:
            yield f"event: routing\ndata: {json.dumps(routing_info, ensure_ascii=False)}\n\n"

        if relevant:
            yield f"event: context\ndata: {json.dumps({'categories': routing_info.get('categories', []), 'relevant_contexts': relevant, 'algorithm': embedding_algorithm}, ensure_ascii=False)}\n\n"

        if extra_context:
            messages.append({"role": "system", "content": f"Reference Context:\n{extra_context}"})

        messages.append({"role": "user", "content": message})

        try:
            stream = self.client.chat.completions.create(model=self.model, messages=messages, temperature=0.7, stream=True)

            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield f"data: {delta}\n\n"

            yield "event: done\ndata: end\n\n"

        except Exception as e:
            yield f"event: error\ndata: {str(e)}\n\n"
