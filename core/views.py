from django.shortcuts import render, get_object_or_404

from .models import Article


def home(request):
    articles = Article.objects.filter(status="PUBLISHED").select_related("author", "artist")
    featured = articles.first()
    rest = articles[1:13] if featured else articles[:12]

    return render(request, "index.html", {
        "featured": featured,
        "articles": rest,
    })


def article_detail(request, slug):
    article = get_object_or_404(
        Article.objects.select_related("author", "artist"),
        slug=slug,
        status="PUBLISHED",
    )

    related = (
        Article.objects.filter(status="PUBLISHED", category=article.category)
        .exclude(id=article.id)
        .order_by("-published_at")[:3]
    )

    return render(request, "article_detail.html", {
        "article": article,
        "related": related,
    })


def article_category(request, category):
    valid_categories = dict(Article.CATEGORY_CHOICES)
    category = category.upper()
    if category not in valid_categories:
        from django.http import Http404
        raise Http404("Unknown category")

    articles = Article.objects.filter(status="PUBLISHED", category=category).select_related("author", "artist")

    return render(request, "category.html", {
        "category": category,
        "category_label": valid_categories[category],
        "articles": articles,
    })
