import logging

from bs4 import BeautifulSoup
from requests import RequestException

from constants import EXPECTED_STATUS
from exceptions import ParserFindTagException


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(f'Возникла ошибка при загрузке страницы {url}',
                          stack_info=True)


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if not searched_tag:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag


def get_status(session, preview_status, url):
    response = get_response(session, url)
    soup = BeautifulSoup(response.text, features='lxml')
    word_status_tag = soup.find(string='Status').parent
    status_tag = word_status_tag.find_next_sibling('dd')
    actual_status = status_tag.abbr.text
    expected_statuses = EXPECTED_STATUS[preview_status]
    if actual_status not in expected_statuses:
        error_msg = (
            f'Несовпадающие статусы:\n{url}\n'
            f'Статус в карточке: {actual_status}\n'
            f'Ожидаемые статусы: {expected_statuses}'
        )
        logging.error(error_msg)
    return actual_status
