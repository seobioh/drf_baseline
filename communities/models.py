# communities/models.py
app_name = "communities"

from django.db import models
from django.core.exceptions import ValidationError

from accounts.models import User

# Community
# <-------------------------------------------------------------------------------------------------------------------------------->
class Community(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)

    member_count = models.IntegerField(default=0)
    favorite_count = models.IntegerField(default=0)
    post_count = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Communities" 


class Member(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='members')
    nickname = models.CharField(max_length=24, blank=True)

    profile_image = models.TextField(null=True, blank=True)

    follower_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    post_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    scrap_count = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    last_access = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)

    class Meta:
        unique_together = (('user', 'community'), ('community', 'nickname'))

    def __str__(self):
        return f"{self.user.email} in {self.community.name}"


class CommunityFavorite(models.Model):
    id = models.AutoField(primary_key=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='community_favorites')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='community_favorites')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('community', 'member')
        verbose_name = "Community Favorite"
        verbose_name_plural = "Community Favorites"

    def __str__(self):
        return f"{self.member.nickname} favored {self.community.name}"


class FollowStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    ACCEPTED = 'ACCEPTED', 'Accepted'
    BLOCKED = 'BLOCKED', 'Blocked'


class Follow(models.Model):
    follower = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='followings') # 내가 팔로우 하는 사람들
    following = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='followers') # 나를 팔로우 하는 사람들
    status = models.CharField(max_length=10, choices=FollowStatus.choices, default=FollowStatus.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.nickname} → {self.status})"


# Post
# <-------------------------------------------------------------------------------------------------------------------------------->
class PostCategory(models.Model):
    id = models.AutoField(primary_key=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='post_categories')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='post_subcategories', null=True, blank=True)
    name = models.CharField(max_length=100)

    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)

    favorite_count = models.IntegerField(default=0)
    post_count = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    def clean(self):
        if self.parent and self.parent.community != self.community:
            raise ValidationError("Parent category must belong to the same community.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"[{self.community.name}] {self.name}"

    class Meta:
        unique_together = ('community', 'name')
        verbose_name_plural = "Post Categories" 


class PostCategoryFavorite(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(PostCategory, on_delete=models.CASCADE, related_name='post_category_favorites')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='post_category_favorites')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('category', 'member')
        verbose_name = "Post Category Favorite"
        verbose_name_plural = "Post Category Favorites"

    def __str__(self):
        return f"{self.member.nickname} liked {self.category.name}"


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(PostCategory, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)

    content = models.TextField()
    images = models.JSONField(blank=True, null=True)

    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    scrap_count = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    access_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} by {'익명' if self.is_anonymous else self.author.nickname}"
    

class PostLike(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='post_likes')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'member')
        verbose_name = "Post Like"
        verbose_name_plural = "Post Likes"

    def __str__(self):
        return f"{self.member.nickname} liked {self.post.title}"
    

class PostScrap(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_scraps')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='post_scraps')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'member')
        verbose_name = "Post Scrap"
        verbose_name_plural = "Post Scraps"

    def __str__(self):
        return f"{self.member.nickname} scraped {self.post.title}"


class PostComment(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments')
    author = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='post_comments')

    content = models.TextField()
    image = models.CharField(max_length=255, blank=True, null=True)

    like_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment by {'익명' if self.is_anonymous else self.author.nickname} on {self.post.title}"
    
    def soft_delete(self):
        self.is_active = False
        self.content = "삭제된 댓글입니다."
        self.save()

    class Meta:
        verbose_name_plural = "Post Comments"
        ordering = ['-id']


class PostCommentLike(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='post_comment_likes')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='post_comment_likes')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'member')  # 유저당 한 댓글에 한 번만 좋아요
        verbose_name = "Post Comment Like"
        verbose_name_plural = "Post Comment Likes"

    def __str__(self):
        return f"{self.member.nickname} likes Comment {self.comment.id}"


class PostReply(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, related_name='post_replies')
    author = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='post_replies')

    content = models.TextField()
    image = models.CharField(max_length=255, blank=True, null=True)

    like_count = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)

    def __str__(self):
        return f"Reply by {'익명' if self.is_anonymous else self.author.nickname} on comment {self.comment.id}"
 
    class Meta:
        verbose_name_plural = "Post Replies"    


class PostReplyLike(models.Model):
    id = models.AutoField(primary_key=True)
    reply = models.ForeignKey(PostReply, on_delete=models.CASCADE, related_name='post_reply_likes')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='post_reply_likes')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('reply', 'member')  # 유저당 한 대댓글에 한 번만 좋아요
        verbose_name = "Post Reply Like"
        verbose_name_plural = "Post Reply Likes"

    def __str__(self):
        return f"{self.member.nickname} likes Reply {self.reply.id}"
    

