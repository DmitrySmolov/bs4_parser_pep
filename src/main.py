from collections import Counter
import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests_cache import CachedSession
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, BS4_FEATURE, DL_LINK_PATTERN, HTMLTag,
                       MAIN_DOC_URL, MAIN_PEPS_URL, PY_VERSION_STATUS_PATTERN)
from outputs import control_output
from utils import find_tag, get_response, get_status


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if not response:
        return
    soup = BeautifulSoup(response.text, features=BS4_FEATURE)
    main_div = find_tag(soup, HTMLTag.SECTION,
                        attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, HTMLTag.DIV,
                           attrs={'class': 'toctree-wrapper compound'})
    sections_by_python = div_with_ul.find_all(
        HTMLTag.LI, attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, HTMLTag.A)
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if not response:
            continue
        soup = BeautifulSoup(response.text, features=BS4_FEATURE)
        h1, dl = find_tag(soup, HTMLTag.H1), find_tag(soup, HTMLTag.DL)
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))

    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if not response:
        return
    soup = BeautifulSoup(response.text, features=BS4_FEATURE)
    sidebar = find_tag(soup, HTMLTag.DIV,
                       attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all(HTMLTag.UL)
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all(HTMLTag.A)
            break
        raise Exception('Не найден список c версиями Python')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = PY_VERSION_STATUS_PATTERN
    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        if text_match:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        link = a_tag['href']
        results.append((link, version, status))

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if not response:
        return
    soup = BeautifulSoup(response.text, features=BS4_FEATURE)
    main_tag = find_tag(soup, HTMLTag.DIV, attrs={'role': 'main'})
    table_tag = find_tag(main_tag, HTMLTag.TABLE, attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(table_tag, HTMLTag.A,
                          attrs={'href': re.compile(DL_LINK_PATTERN)})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    response = get_response(session, MAIN_PEPS_URL)
    if not response:
        return
    soup = BeautifulSoup(response.text, features=BS4_FEATURE)
    num_idx_section = find_tag(soup, HTMLTag.SECTION,
                               attrs={'id': 'numerical-index'})
    table_body = find_tag(num_idx_section, HTMLTag.TBODY)
    peps = table_body.find_all(HTMLTag.TR,
                               attrs={'class': re.compile(r'row-(odd|even)')})
    actual_statuses = Counter()
    results = [('Статус', 'Количество')]
    for pep in tqdm(peps):
        abbr = find_tag(pep, HTMLTag.ABBR).text
        preview_status = abbr[1:]
        pep_link = find_tag(pep, HTMLTag.A)['href']
        pep_url = urljoin(MAIN_PEPS_URL, pep_link)
        actual_status = get_status(session, preview_status, pep_url)
        actual_statuses[actual_status] += 1
    for status, quantity in actual_statuses.items():
        results.append((status, quantity))
    results.append(('Total', sum(actual_statuses.values())))

    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if parser_mode == 'pep':
        args.output = 'file'

    if results:
        control_output(results, args)

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
