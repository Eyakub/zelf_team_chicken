from django.db import models

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Author(TimestampedModel):
    """
    TODO: When the data is being created or updated we don't know, need to add that information
    """
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    unique_id = models.CharField(max_length=1024, db_index=True, unique=True)
    url = models.CharField(max_length=1024, blank=True, )
    title = models.CharField(max_length=1024, blank=True, )
    big_metadata = models.JSONField(blank=True, null=True)
    secret_value = models.JSONField(blank=True, null=True)
    followers = models.IntegerField(default=0)


class Content(TimestampedModel):
    """
    TODO: When the data is being created or updated we don't know, need to add that information
    """
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    unique_id = models.CharField(max_length=1024, )
    url = models.CharField(max_length=1024, blank=True, )
    title = models.TextField(blank=True)
    like_count = models.BigIntegerField(blank=True, null=False, default=0, )
    comment_count = models.BigIntegerField(blank=True, null=False, default=0, )
    view_count = models.BigIntegerField(blank=True, null=False, default=0, )
    share_count = models.BigIntegerField(blank=True, null=False, default=0, )
    thumbnail_url = models.URLField(max_length=1024, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True, )
    big_metadata = models.JSONField(blank=True, null=True)
    secret_value = models.JSONField(blank=True, null=True)


class Category(models.Model):
    """
    A model representing a category that can have multiple tags.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=['name'])]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    TODO: The tag is being duplicated sometimes, need to do something in the database.
    Filtering
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='tags')

    class Meta:
        indexes = [models.Index(fields=['name'])]

    def __str__(self):
        return self.name


class ContentTag(models.Model):
    """
    TODO: The content and tag is being duplicated, need to do something in the database
    """
    content = models.ForeignKey(Content, on_delete=models.CASCADE,
                                related_name='content_tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE,
                            related_name='content_tags')

    class Meta:
        unique_together = ('content', 'tag')
        indexes = [
            models.Index(fields=['content']),
            models.Index(fields=['tag']),
        ]

    def __str__(self):
        return f"{self.content.title} - {self.tag.name}"
