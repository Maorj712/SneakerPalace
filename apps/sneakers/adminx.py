import xadmin
from sneakers.models import Sneakers


class SneakersAdmin(object):
    list_display = ['brand', 'name', 'style', 'image', 'retail_price', 'retail_date', 'click_nums', 'fav_nums',
                    'add_time']
    search_fields = ['brand', 'name', 'style', 'image', 'retail_price', 'retail_date', 'click_nums', 'fav_nums']
    list_filter = ['brand', 'name', 'style', 'image', 'retail_price', 'retail_date', 'click_nums', 'fav_nums',
                   'add_time']


xadmin.site.register(Sneakers, SneakersAdmin)
