# communities/admin.py
app_name = 'communities'

from django.contrib import admin

from .models import Community, Member, CommunityFavorite, Follow
from .models import PostCategory, PostCategoryFavorite, Post, PostLike, PostScrap, PostComment, PostCommentLike, PostReply, PostReplyLike

# Community
# <-------------------------------------------------------------------------------------------------------------------------------->
@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'member_count', 'favorite_count', 'post_count', 'score', 'is_active', 'created_at', 'modified_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-id',)
    readonly_fields = ('member_count', 'favorite_count', 'post_count', 'created_at', 'modified_at')

    fieldsets = (
        ('Basic', {'fields': ('name', 'description', 'image')}),
        ('Counts', {'fields': ('member_count', 'favorite_count', 'post_count', 'score')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'modified_at')}),
    )


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'nickname', 'user', 'community', 'is_active', 'is_staff', 'is_admin', 'is_private', 'created_at')
    list_filter = ('is_active', 'is_staff', 'is_admin', 'is_private', 'created_at')
    search_fields = ('nickname', 'user__email', 'community__name')
    ordering = ('-id',)
    raw_id_fields = ('user', 'community')
    readonly_fields = (
        'follower_count', 'following_count', 'post_count', 'like_count',
        'comment_count', 'reply_count', 'scrap_count', 'created_at', 'modified_at', 'last_access'
    )

    fieldsets = (
        ('Basic', {'fields': ('user', 'community', 'nickname', 'profile_image')}),
        ('Counts', {'fields': ('follower_count', 'following_count', 'post_count', 'like_count', 'comment_count', 'reply_count', 'scrap_count', 'score')}),
        ('Status', {'fields': ('is_active', 'is_staff', 'is_admin', 'is_private')}),
        ('Timestamps', {'fields': ('created_at', 'modified_at', 'last_access')}),
    )


@admin.register(CommunityFavorite)
class FavoriteCommunityAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'community', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('member__nickname', 'community__name')
    raw_id_fields = ('member', 'community')
    readonly_fields = ('created_at',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'following', 'status', 'created_at', 'modified_at')
    list_filter = ('status', 'created_at')
    list_editable = ('status',)
    search_fields = ('follower__nickname', 'following__nickname')
    raw_id_fields = ('follower', 'following')
    readonly_fields = ('created_at', 'modified_at')


# Post
# <-------------------------------------------------------------------------------------------------------------------------------->
@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'community', 'parent', 'is_active', 'favorite_count', 'post_count', 'created_at', 'modified_at')
    list_filter = ('community', 'is_active', 'created_at')
    search_fields = ('name', 'community__name')
    ordering = ('-id',)
    raw_id_fields = ('community', 'parent')
    readonly_fields = ('favorite_count', 'post_count', 'score', 'created_at', 'modified_at')

    fieldsets = (
        ('Basic', {'fields': ('community', 'parent', 'name', 'description', 'image')}),
        ('Counts', {'fields': ('favorite_count', 'post_count', 'score')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'modified_at')}),
    )


@admin.register(PostCategoryFavorite)
class PostCategoryFavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'category', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('member__nickname', 'category__name')
    raw_id_fields = ('member', 'category')
    readonly_fields = ('created_at',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'category', 'is_verified', 'is_anonymous', 'is_active', 'access_count', 'created_at', 'modified_at')
    list_filter = ('category', 'is_verified', 'is_anonymous', 'is_active', 'created_at')
    search_fields = ('title', 'content', 'author__nickname')
    ordering = ('-id',)
    raw_id_fields = ('category', 'author')
    readonly_fields = ('like_count', 'comment_count', 'reply_count', 'scrap_count', 'score', 'created_at', 'modified_at')

    fieldsets = (
        ('Basic', {'fields': ('category', 'author', 'title', 'content', 'images')}),
        ('Counts', {'fields': ('like_count', 'comment_count', 'reply_count', 'scrap_count', 'score', 'access_count')}),
        ('Status', {'fields': ('is_active', 'is_verified', 'is_anonymous')}),
        ('Timestamps', {'fields': ('created_at', 'modified_at')}),
    )


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('member__nickname', 'post__title')
    raw_id_fields = ('member', 'post')
    readonly_fields = ('created_at',)


@admin.register(PostScrap)
class PostScrapAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('member__nickname', 'post__title')
    raw_id_fields = ('member', 'post')
    readonly_fields = ('created_at',)


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'post', 'content_preview', 'is_anonymous', 'is_active', 'is_verified', 'created_at', 'modified_at')
    list_filter = ('is_active', 'is_verified', 'is_anonymous', 'created_at')
    list_editable = ('is_active',)
    search_fields = ('author__nickname', 'post__title', 'content')
    raw_id_fields = ('post', 'author')
    readonly_fields = ('like_count', 'reply_count', 'score', 'created_at', 'modified_at')

    fieldsets = (
        ('Basic', {'fields': ('post', 'author', 'content', 'image')}),
        ('Counts', {'fields': ('like_count', 'reply_count', 'score')}),
        ('Status', {'fields': ('is_active', 'is_verified', 'is_anonymous')}),
        ('Timestamps', {'fields': ('created_at', 'modified_at')}),
    )

    def content_preview(self, obj):
        if not obj.content:
            return ''
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    content_preview.short_description = 'Content'


@admin.register(PostCommentLike)
class PostCommentLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'comment', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('member__nickname', 'comment__content')
    raw_id_fields = ('member', 'comment')
    readonly_fields = ('created_at',)


@admin.register(PostReply)
class PostReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'comment', 'content_preview', 'is_anonymous', 'is_active', 'is_verified', 'created_at', 'modified_at')
    list_filter = ('is_active', 'is_verified', 'is_anonymous', 'created_at')
    list_editable = ('is_active',)
    search_fields = ('author__nickname', 'content', 'comment__content')
    raw_id_fields = ('comment', 'author')
    readonly_fields = ('like_count', 'score', 'created_at', 'modified_at')

    fieldsets = (
        ('Basic', {'fields': ('comment', 'author', 'content', 'image')}),
        ('Counts', {'fields': ('like_count', 'score')}),
        ('Status', {'fields': ('is_active', 'is_verified', 'is_anonymous')}),
        ('Timestamps', {'fields': ('created_at', 'modified_at')}),
    )

    def content_preview(self, obj):
        if not obj.content:
            return ''
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    content_preview.short_description = 'Content'


@admin.register(PostReplyLike)
class PostReplyLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'reply', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('member__nickname',)
    raw_id_fields = ('member', 'reply')
    readonly_fields = ('created_at',)
