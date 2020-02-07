from django.db import models
from DjangoUeditor.models import UEditorField

from datetime import datetime


# Create your models here.


class Blog(models.Model):
    title = models.CharField(max_length=50, default="", verbose_name="文章标题")
    content = UEditorField(verbose_name="文章内容", width=600, height=300, imagePath="blog/ueditor/",
                           filePath="blog/ueditor/", default="")
    image = models.ImageField(upload_to="blog/%Y/%m", verbose_name="文章封面图", max_length=100)
    click_nums = models.IntegerField(default=0, verbose_name="浏览次数")
    fav_nums = models.IntegerField(default=0, verbose_name="收藏数")
    release_time = models.CharField(default="", verbose_name="文章发布时间", max_length=20)
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "资讯文章"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
