from enum import Enum
from pathlib import Path

BASE_DIR = Path(__file__).parent

BS4_FEATURE = 'lxml'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

# Шаблон поиска ссылки для скачивания файла в нужном формате
# (в данном случае zip архива pdf файла со страницами размера A4)
DL_LINK_PATTERN = r'.+pdf-a4\.zip$'

DT_FORMAT = '%d.%m.%Y %H:%M:%S'

ENCODING = 'utf-8'

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'

MAIN_DOC_URL = 'https://docs.python.org/3/'

MAIN_PEPS_URL = 'https://peps.python.org/'

# Шаблон для парсинга номера версии и статуса версии из списка версий Python
PY_VERSION_STATUS_PATTERN = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'


class HTMLTag:
    A = 'a'
    ABBR = 'abbr'
    DD = 'dd'
    DIV = 'div'
    DL = 'dl'
    H1 = 'h1'
    LI = 'li'
    SECTION = 'section'
    TABLE = 'table'
    TBODY = 'tbody'
    TR = 'tr'
    UL = 'ul'


class OutputType(str, Enum):
    PRETTY = 'pretty'
    FILE = 'file'
