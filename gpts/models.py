# gpts/models.py
app_name = "gpts"

from django.db import models

from accounts.models import User

class GPTPrompt(models.Model):
    name = models.CharField(max_length=100)
    prompt = models.TextField()
    description = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'GPT Prompt'
        verbose_name_plural = 'GPT Prompts'

    def __str__(self):
        return f'({self.name} - {self.prompt})'


class GPTChatRoom(models.Model):
    name = models.CharField(max_length=100, default="새 채팅방")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt = models.ForeignKey(GPTPrompt, on_delete=models.SET_NULL, null=True, blank=True)

    summary = models.TextField(null=True, blank=True)
    summary_token_count = models.IntegerField(default=0)
    last_summarized_message = models.ForeignKey("GPTChatMessage", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'GPT Chat Room'
        verbose_name_plural = 'GPT Chat Rooms'

    def __str__(self):
        return f'{[self.id]} {self.name} - {self.user.email}'

    def save(self, *args, **kwargs):
        if self.summary:
            self.summary_token_count = len(self.summary) // 4
        super().save(*args, **kwargs)


class GPTChatMessage(models.Model):
    ROLE_CHOICES = (
        ('system', 'System'),
        ('user', 'User'),
        ('assistant', 'Assistant'),
    )

    MODEL_CHOICES = (
        ('gpt-4o-mini', 'GPT-4o-mini'),
        ('gpt-4o', 'GPT-4o'),
        ('gpt-4o-turbo', 'GPT-4o-turbo'),
    )

    chat_room = models.ForeignKey(GPTChatRoom, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    model = models.CharField(max_length=100, choices=MODEL_CHOICES, default='gpt-4o-mini')

    message = models.TextField()
    token_count = models.IntegerField(default=0)
    is_error = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'GPT Chat Message'
        verbose_name_plural = 'GPT Chat Messages'

    def save(self, *args, **kwargs):
        if self.message:
            self.token_count = len(self.message) // 4
        super().save(*args, **kwargs)