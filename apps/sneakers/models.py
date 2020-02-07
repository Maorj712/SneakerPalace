from django.db import models

from datetime import datetime


# Create your models here.


class Sneakers(models.Model):
    id_in_du = models.IntegerField(primary_key=True, verbose_name="毒产品ID")
    brand = models.CharField(max_length=10,
                             choices=(("Jordan", "Jordan"), ("Nike", "Nike"), ("Adidas", "Adidas"), ("Yeezy", "Yeezy")),
                             default="Jordan", verbose_name="球鞋品牌")
    name = models.CharField(max_length=100, default="", verbose_name="球鞋名称")
    style = models.CharField(max_length=50, default="", verbose_name="球鞋货号")
    image = models.ImageField(upload_to="sneakers/%Y/%m", verbose_name="球鞋图片", max_length=100)
    sold_nums = models.IntegerField(default=0, verbose_name="销售量")
    retail_price = models.IntegerField(default=0, verbose_name="发售价")
    retail_date = models.CharField(max_length=50, default="", verbose_name="发售日期")
    click_nums = models.IntegerField(default=0, verbose_name="点击数")
    fav_nums = models.IntegerField(default=0, verbose_name="收藏数")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "球鞋信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Price(models.Model):
    id_in_du = models.ForeignKey(Sneakers, verbose_name="毒产品ID", on_delete=models.CASCADE)
    style = models.CharField(max_length=50, default="", verbose_name="球鞋货号")
    size = models.FloatField(default=0, verbose_name="尺码")
    price = models.IntegerField(default=0, verbose_name="价格")

    class Meta:
        verbose_name = "球鞋价格"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.size



