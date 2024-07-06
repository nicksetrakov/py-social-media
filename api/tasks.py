from celery import shared_task

from .models import Post


@shared_task
def create_scheduled_post(post_id):

    post = Post.objects.get(pk=post_id)
    post.published = True
    post.save()
