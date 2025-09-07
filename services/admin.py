# services/admin.py
app_name = "services"

from django.contrib import admin

from .models import Notice, Event, Ad, FAQ, PrivacyPolicy, Term

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('service', 'title', 'subtitle', 'start_date', 'end_date', 'is_active', 'created_at')
    list_filter = ('service', 'is_active', 'created_at', 'start_date', 'end_date')
    search_fields = ('title', 'subtitle', 'description')
    list_editable = ('is_active',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('service', 'title', 'subtitle', 'description')
        }),
        ('Images', {
            'fields': ('mobile_img', 'desktop_img', 'detail_img'),
            'classes': ('collapse',)
        }),
        ('Link', {
            'fields': ('link',),
            'classes': ('collapse',)
        }),
        ('Period', {
            'fields': ('start_date', 'end_date')
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('service', 'title', 'subtitle', 'start_date', 'end_date', 'is_active', 'created_at')
    list_filter = ('service', 'is_active', 'created_at', 'start_date', 'end_date')
    search_fields = ('title', 'subtitle', 'description')
    list_editable = ('is_active',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('service', 'title', 'subtitle', 'description')
        }),
        ('Images', {
            'fields': ('mobile_img', 'desktop_img', 'detail_img'),
            'classes': ('collapse',)
        }),
        ('Link', {
            'fields': ('link',),
            'classes': ('collapse',)
        }),
        ('Period', {
            'fields': ('start_date', 'end_date')
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('service', 'title', 'subtitle', 'start_date', 'end_date', 'is_active', 'created_at')
    list_filter = ('service', 'is_active', 'created_at', 'start_date', 'end_date')
    search_fields = ('title', 'subtitle', 'description')
    list_editable = ('is_active',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('service', 'title', 'subtitle', 'description')
        }),
        ('Images', {
            'fields': ('mobile_img', 'desktop_img', 'detail_img'),
            'classes': ('collapse',)
        }),
        ('Link', {
            'fields': ('link',),
            'classes': ('collapse',)
        }),
        ('Period', {
            'fields': ('start_date', 'end_date')
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('service', 'order', 'question', 'is_active', 'created_at')
    list_filter = ('service', 'is_active', 'created_at')
    search_fields = ('question', 'answer')
    list_editable = ('order', 'is_active')
    ordering = ('service', 'order')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('service', 'order', 'question', 'answer')
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )


@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ('service', 'order', 'subject', 'is_active', 'created_at')
    list_filter = ('service', 'is_active', 'created_at')
    search_fields = ('subject', 'detail')
    list_editable = ('order', 'is_active')
    ordering = ('service', 'order')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('service', 'order', 'subject', 'detail')
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('service', 'order', 'subject', 'is_active', 'created_at')
    list_filter = ('service', 'is_active', 'created_at')
    search_fields = ('subject', 'detail')
    list_editable = ('order', 'is_active')
    ordering = ('service', 'order')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('service', 'order', 'subject', 'detail')
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )
