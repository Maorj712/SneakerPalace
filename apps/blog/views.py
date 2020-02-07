from django.shortcuts import render
from django.views.generic.base import View

from blog.models import Blog
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.


class BlogListView(View):

    def get(self, request):
        all_blogs = Blog.objects.all().order_by('-id')

        sort = request.GET.get('sort', '')

        if sort:
            if sort == 'popular':
                all_blogs = Blog.objects.all().order_by('-click_nums')

        # 对资讯列表页进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_blogs, 8, request=request)

        blogs = p.page(page)

        return render(request, "blog-list.html", {
            "all_blogs": blogs,
        })


class BlogDetailView(View):

    def get(self, request, blog_id):
        blog_info = Blog.objects.get(pk=blog_id)
        blog_info.click_nums += 1
        blog_info.save()

        other_blog = Blog.objects.all().order_by('?')[:5]

        return render(request, "blog-details.html", {
            "blog_info": blog_info,
            "other_blog": other_blog,
        })
