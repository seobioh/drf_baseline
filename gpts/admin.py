# gpts/admin.py
app_name = "gpts"

from django.contrib import admin

from .models import GPTPrompt, GPTChatRoom, GPTChatMessage

@admin.register(GPTPrompt)
class GPTPromptAdmin(admin.ModelAdmin):
    list_display = ('name', 'prompt', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    list_editable = ('is_active',)
    search_fields = ('name',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'prompt', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )


class GPTChatMessageInline(admin.TabularInline):
    model = GPTChatMessage
    extra = 0
    readonly_fields = ('token_count', 'created_at')
    fields = ('role', 'model', 'message', 'token_count', 'is_error', 'created_at')


@admin.register(GPTChatRoom)
class GPTChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'prompt', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    list_editable = ('is_active',)
    search_fields = ('name', 'user__email')
    raw_id_fields = ('user', 'prompt', 'last_summarized_message')
    inlines = (GPTChatMessageInline,)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'user', 'prompt')
        }),
        ('Summary', {
            'fields': ('summary', 'summary_token_count', 'last_summarized_message')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'modified_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'modified_at')


@admin.register(GPTChatMessage)
class GPTChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_room', 'role', 'model', 'message_preview', 'token_count', 'is_error', 'created_at')
    list_filter = ('role', 'model', 'is_error', 'created_at')
    search_fields = ('message',)
    raw_id_fields = ('chat_room',)
    readonly_fields = ('token_count', 'created_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('chat_room', 'role', 'model', 'message')
        }),
        ('Metadata', {
            'fields': ('token_count', 'is_error', 'created_at')
        })
    )

    def message_preview(self, obj):
        if not obj.message:
            return ''
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message

    message_preview.short_description = 'Message'