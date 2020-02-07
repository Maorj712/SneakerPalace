from django.shortcuts import render
from django.views.generic.base import View
from django.db.models import Q
from django.http import HttpResponse, JsonResponse

from sneakers.models import Sneakers, Price
from users.models import UserFavorite
from utils.stockx_spider import crawl_stockx

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.


class ProductsListView(View):

    def get(self, request):
        all_sneakers = Sneakers.objects.all().order_by('-sold_nums')

        # 排序
        jordan = Sneakers.objects.filter(brand='Jordan')
        nike = Sneakers.objects.filter(brand='Nike')
        adidas = Sneakers.objects.filter(brand='Adidas')
        yeezy = Sneakers.objects.filter(brand='Yeezy')

        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'new':
                all_sneakers = all_sneakers.order_by('-id_in_du')
            elif sort == 'jordan':
                all_sneakers = jordan.order_by('-sold_nums')
            elif sort == 'nike':
                all_sneakers = nike.order_by('-sold_nums')
            elif sort == 'adidas':
                all_sneakers = adidas.order_by('-sold_nums')
            elif sort == 'yeezy':
                all_sneakers = yeezy.order_by('-sold_nums')

        # 对球鞋进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_sneakers, 15, request=request)

        sneakers = p.page(page)
        return render(request, 'product-list.html', {
            "all_sneakers": sneakers,
            "sort": sort,
        })


class ProductDetailView(View):
    def get(self, request, style):
        sneaker_info = Sneakers.objects.get(style=style)
        sneaker_info.click_nums += 1
        sneaker_info.save()
        sneaker_size = Price.objects.filter(style=style)

        has_fav_product = False

        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=sneaker_info.id_in_du):
                has_fav_product = True

        brand = sneaker_info.brand
        same_product = Sneakers.objects.filter(brand=brand).order_by('?')[:4]

        return render(request, "product-details.html", {
            "sneaker_info": sneaker_info,
            "sneaker_size": sneaker_size,
            "same_product": same_product,
            "has_fav_product": has_fav_product,
        })


class AddFavView(View):
    def post(self, request):
        fav_id = request.POST.get('fav_id', 0)

        if not request.user.is_authenticated:
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')
        exist_records = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id))
        if exist_records:
            # 如果已经存在，则表示用户取消收藏
            exist_records.delete()
            return HttpResponse('{"status":"success", "msg":"取消收藏"}', content_type='application/json')
        else:
            user_fav = UserFavorite()
            if int(fav_id) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.save()
                return HttpResponse('{"status":"success", "msg":"添加收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"fail"}', content_type='application/json')


class RemoveFavView(View):
    def post(self, request):
        fav_id = request.POST.get('fav_id', 0)
        exist_records = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id))
        exist_records.delete()
        return render(request, 'user_center.html', {})


class ComparisonPriceView(View):
    def post(self, request):
        back_list = []
        comparison_style = request.POST.get('comparison_style', '').upper()
        in_dewu = Price.objects.filter(style=comparison_style)
        dewu_list = []
        for i in in_dewu:
            dewu_dict = {}
            dewu_dict['dewu_size'] = i.size
            dewu_dict['dewu_price'] = "￥" + str(i.price)
            dewu_list.append(dewu_dict)

        stockx_list = crawl_stockx.get_product_price(comparison_style)

        try:
            if len(stockx_list) > len(dewu_list):
                for i in range(0, len(stockx_list)):
                    if i > len(dewu_list) - 1:
                        new_dict = {}
                        new_dict['dewu_size'] = 'None'
                        new_dict['dewu_price'] = 0
                        new_dict['stockx_size'] = stockx_list[i]['size']
                        new_dict['stockx_price'] = stockx_list[i]['price']
                        dewu_list.append(new_dict)

                    dewu_list[i]['stockx_size'] = stockx_list[i]['size']
                    dewu_list[i]['stockx_price'] = stockx_list[i]['price']
            else:
                for j in range(0, len(dewu_list)):
                    if j > len(stockx_list) - 1:
                        break
                    dewu_list[j]['stockx_size'] = stockx_list[j]['size']
                    dewu_list[j]['stockx_price'] = stockx_list[j]['price']
            back_list = dewu_list
        except:
            back_list = dewu_list

        return JsonResponse(back_list, safe=False)

    def get(self, request):
        return render(request, 'comparison_price.html')
