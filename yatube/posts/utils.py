from django.core.paginator import Paginator

from yatube.settings import POSTS_SHOW


def paginator_arrange(request, post_list):
    paginator = Paginator(post_list, POSTS_SHOW)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
