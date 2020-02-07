from django.conf.urls import url, include
from sneakers.views import ProductsListView, ProductDetailView, AddFavView, RemoveFavView, ComparisonPriceView

urlpatterns = [
    url(r'^list/$', ProductsListView.as_view(), name="products_list"),
    url(r'^detail/(?P<style>.*)/$', ProductDetailView.as_view(), name="products_detail"),
    url(r'^comparison/$', ComparisonPriceView.as_view(), name="products_comparison"),

    # 收藏
    url(r'^add_fav/$', AddFavView.as_view(), name="add_fav"),
    url(r'^remove_fav/$', RemoveFavView.as_view(), name="remove_fav"),
]
