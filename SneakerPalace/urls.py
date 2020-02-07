"""SneakerPalace URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.views.static import serve
import os

import xadmin

from users.views import LoginView, RegisterView, UserCenterView, ForgetView, ResetView, ModifyPwdView, IndexView, \
    SearchView, LogoutView, ContactView
from SneakerPalace.settings import MEDIA_ROOT, STATIC_ROOT


urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),

    # 富文本相关url
    url(r'^ueditor/', include(('DjangoUeditor.urls', 'ueditor'), namespace='ueditor')),

    url(r'^$', IndexView.as_view(), name="index"),
    url(r'^user_center/$', UserCenterView.as_view(), name="user_center"),
    url(r'^login/$', LoginView.as_view(), name="login"),
    url(r'^logout/$', LogoutView.as_view(), name="logout"),
    url(r'^register/$', RegisterView.as_view(), name="register"),
    url(r'^forget/$', ForgetView.as_view(), name="forget"),
    url(r'^reset/(?P<active_code>.*)/$', ResetView.as_view(), name="reset"),
    url(r'^modify_pwd/$', ModifyPwdView.as_view(), name="modify_pwd"),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^search/$', SearchView.as_view(), name="search"),
    url(r'^contact/$', ContactView.as_view(), name="contact"),

    url(r'^products/', include(('sneakers.urls', 'sneakers'), namespace="products")),
    url(r'^blog/', include(('blog.urls', 'blog'), namespace="blog")),

    # 配置上传文件的访问处理函数
    url(r'media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),

    url(r'static/(?P<path>.*)$', serve, {"document_root": STATIC_ROOT}),
]
handler404 = 'users.views.page_not_found'
handler500 = 'users.views.page_error'
