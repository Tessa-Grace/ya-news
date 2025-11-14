import pytest

from django.urls import reverse
from http import HTTPStatus

from pytest_django.asserts import assertRedirects

from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_authenticated_user_can_create_comment(
    author_client,
    author,
    form_data,
    news
):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = author_client.post(url, data=form_data)
    assertRedirects(
        response,
        reverse('news:detail', kwargs={'pk': news.pk})
    )


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    bad_words_data = {'text': 'Текст содержит слово редиска'}
    response = author_client.post(url, data=bad_words_data)
    assert Comment.objects.count() == 0
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, form_data, comment, news):
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = author_client.post(url, data=form_data)
    assertRedirects(response, reverse('news:detail', kwargs={'pk': news.pk}))


@pytest.mark.django_db
def test_other_user_cant_edit_comment(not_author_client, form_data, comment):
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    original_text = comment.text
    response = not_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == original_text


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment_pk_for_args, news):
    url = reverse('news:delete', args=comment_pk_for_args)
    response = author_client.post(url)
    assertRedirects(response, reverse('news:detail', kwargs={'pk': news.pk}))


@pytest.mark.django_db
def test_other_user_cant_delete_comment(
    not_author_client,
    comment_pk_for_args
):
    url = reverse('news:delete', args=comment_pk_for_args)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
