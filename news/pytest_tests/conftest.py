import pytest
from datetime import datetime, timedelta
from django.test.client import Client

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def news(author):
    news = News.objects.create(
        title='Заголовок новости',
        text='Текст новости',
        date=datetime.today(),
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def pk_for_args(news):
    return (news.pk,)


@pytest.fixture
def comment_pk_for_args(comment):
    return (comment.pk,)


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст комментария'
    }


@pytest.fixture
def multiple_news():
    today = datetime.today()
    news_list = []
    for i in range(15):
        news = News.objects.create(
            title=f'Новость {i}',
            text=f'Текст новости {i}',
            date=today - timedelta(days=i)
        )
        news_list.append(news)
    return news_list


@pytest.fixture
def multiple_comments(news, author):
    comments = []
    for i in range(5):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i}'
        )
        comments.append(comment)
    return comments
