from django.contrib import admin

from api.models import Post, Comment, Hashtag, Like

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Hashtag)
admin.site.register(Like)
