from django.conf.urls import url, include
from blog.views import BlogListView, BlogDetailView

urlpatterns = [
    url(r'^list/$', BlogListView.as_view(), name="blog_list"),
    url(r'^detail/(?P<blog_id>.*)/$', BlogDetailView.as_view(), name="blog_detail"),
]
