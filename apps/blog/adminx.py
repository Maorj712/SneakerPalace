import xadmin
from blog.models import Blog


class BlogAdmin(object):
    list_display = ['title', 'content', 'image', 'click_nums', 'fav_nums', 'add_time']
    search_fields = ['title', 'content', 'image', 'click_nums', 'fav_nums']
    list_filter = ['title', 'content', 'image', 'click_nums', 'fav_nums', 'add_time']
    style_fields = {'content': 'ueditor'}


xadmin.site.register(Blog, BlogAdmin)
