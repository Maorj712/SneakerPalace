from django.shortcuts import render
from django.views.generic.base import View
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from utils.email_send import send_register_email
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.backends import ModelBackend

from users.forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm
from users.models import UserProfile, EmailVerifyRecord, Banner, UserFavorite
from sneakers.models import Sneakers
from blog.models import Blog
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.


class UserCenterView(View):

    def get(self, request):
        sneakers_list = []
        user_name = request.user.username
        fav_sneakers = UserFavorite.objects.filter(user=request.user)
        for fav_sneaker in fav_sneakers:
            sneaker_id = fav_sneaker.fav_id
            sneaker = Sneakers.objects.get(id_in_du=sneaker_id)
            sneakers_list.append(sneaker)

        return render(request, 'user_center.html', {
            "user_name": user_name,
            "sneakers_list": sneakers_list,
        })


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("index"))


class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class LoginView(View):

    def get(self, request):
        return render(request, "login.html", {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "login.html", {"msg": "用户名或密码错误！"})
        else:
            return render(request, "login.html", {"login_form": login_form})


class RegisterView(View):

    def get(self, request):
        register_form = RegisterForm()
        return render(request, "register.html", {"register_form": register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get("username", "")
            email = request.POST.get("email", "")
            if UserProfile.objects.filter(username=user_name):
                return render(request, "register.html", {"register_form": register_form, "msg": "用户名已存在", })
            if UserProfile.objects.filter(email=email):
                return render(request, "register.html", {"register_form": register_form, "msg": "邮箱已存在", })
            pass_word = request.POST.get("password", "")
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = email
            user_profile.password = make_password(pass_word)
            user_profile.save()
            return render(request, "login.html")
        else:
            return render(request, "register.html", {"register_form": register_form})


class ForgetView(View):

    def get(self, request):
        forget_form = ForgetForm()
        return render(request, "forget.html", {"forget_form": forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            user_name = request.POST.get("email", "")
            if not UserProfile.objects.filter(email=user_name):
                return render(request, "forget.html", {'forget_form': forget_form, "msg": "用户未注册！"})
            send_register_email(user_name, send_type="forget")
            return render(request, "forget.html", {'forget_form': forget_form, "msg": "找回密码邮件发送成功！"})
        else:
            return render(request, "forget.html", {'forget_form': forget_form})


class ResetView(View):

    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, "password_reset.html", {"email": email})
        else:
            return render(request, "active_fail.html")
        return render(request, "login.html")


class ModifyPwdView(View):

    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            email = request.POST.get("email", "")
            if pwd1 != pwd2:
                return render(request, "password_reset.html", {"email": email, "msg": "两次密码输入不一致，请重新输入"})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd1)
            user.save()

            return HttpResponseRedirect(reverse("login"))
        else:
            email = request.POST.get("email", "")
            return render(request, "password_reset.html", {"email": email, "modify_form": modify_form})


class IndexView(View):
    def get(self, request):
        all_banners = Banner.objects.all().order_by('index')

        hot_shoes = Sneakers.objects.all().order_by('-click_nums')[:15]

        new_blog = Blog.objects.all().order_by('-id')[:3]

        return render(request, 'index.html', {
            "all_banners": all_banners,
            "hot_shoes": hot_shoes,
            "new_blog": new_blog,
        })


class SearchView(View):
    def get(self, request):
        # 全局搜索
        all_sneakers = Sneakers.objects.all().order_by('-sold_nums')
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_sneakers = all_sneakers.filter(Q(name__icontains=search_keywords) | Q(style__icontains=search_keywords))

        # 对球鞋进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_sneakers, 30, request=request)

        sneakers = p.page(page)
        return render(request, 'search.html', {
            "all_sneakers": sneakers,
        })


class ContactView(View):
    def get(self, request):
        return render(request, "contact.html")


def page_not_found(request):
    # 404页面处理
    from django.shortcuts import render_to_response
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


def page_error(request):
    # 404页面处理
    from django.shortcuts import render_to_response
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response
