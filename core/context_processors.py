from .models import Article


def nav_categories(request):
    return {"nav_categories": Article.CATEGORY_CHOICES}
