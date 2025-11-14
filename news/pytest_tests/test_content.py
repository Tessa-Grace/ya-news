import pytest
from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm


def test_news_count_on_home_page(client, multiple_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_sorted_from_new_to_old(client, multiple_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    sorted_dates = sorted(dates, reverse=True)
    assert dates == sorted_dates


def test_comments_sorted_by_created_time(client, news, multiple_comments):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    news_obj = response.context['object']
    comments = news_obj.comment_set.all()
    created_times = [comment.created for comment in comments]
    sorted_times = sorted(created_times)
    assert list(created_times) == sorted_times


@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_comment_form_availability_for_different_users(
    news, parametrized_client, form_in_context
):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = parametrized_client.get(url)
    has_form = 'form' in response.context
    assert has_form == form_in_context
    if has_form:
        assert isinstance(response.context['form'], CommentForm)


def test_home_page_available(client):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == 200


def test_news_detail_page_available(client, news):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert response.status_code == 200


def test_news_object_in_context_for_anonymous_user(client, news):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert response.context['object'] == news


def test_comment_pages_contain_comment(author_client, comment):
    urls = [
        reverse('news:edit', kwargs={'pk': comment.pk}),
        reverse('news:delete', kwargs={'pk': comment.pk}),
    ]

    for url in urls:
        response = author_client.get(url)
        assert response.context['object'] == comment


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_pk_for_args')),
        ('news:delete', pytest.lazy_fixture('comment_pk_for_args')),
    )
)
def test_comment_pages_contain_form(author_client, name, args):
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert 'form' in response.context
    if name == 'news:edit':
        assert isinstance(response.context['form'], CommentForm)


def test_auth_pages_available(client):
    urls = [
        reverse('users:login'),
        reverse('users:logout'),
        reverse('users:signup'),
    ]

    for url in urls:
        response = client.get(url)
        assert response.status_code == 200


def test_news_list_context_structure(client, multiple_news):
    url = reverse('news:home')
    response = client.get(url)
    assert 'object_list' in response.context
    assert 'news_list' not in response.context


def test_news_detail_context_structure(client, news):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert 'object' in response.context
    assert 'news' not in response.context
