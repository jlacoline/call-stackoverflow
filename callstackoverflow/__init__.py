import os
import logging
import logging.config

from . import builders
from .testers import apply_tests
from .stackoverflow_parsing import find_stackoverflow_answers
from . import web

M_SEARCH_FOR_DEF = builders.search_for_def_keyword
M_PARSE_SHELL_SCRIPTS = builders.make_functions_from_shell_scripts
M_READ_DOCUMENTATION_LINKS = builders.make_functions_from_documentation_links
M_ALL = [M_READ_DOCUMENTATION_LINKS, M_SEARCH_FOR_DEF, M_PARSE_SHELL_SCRIPTS]


level = os.environ.get("CALLSTACKOVERFLOW_LOGLEVEL", logging.CRITICAL)
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(levelname)s - %(name)s - %(message)s'}},
    'loggers': {'': {'handlers': ['default'], 'level': level},
                'urllib3': {'level': logging.WARNING}},
    'handlers': {'default': {
        'level': level,
        'formatter': 'default',
        'class': 'logging.StreamHandler'}}
})
logger = logging.getLogger(__name__)


def build_functions(query, methods):
    for raw_html in web.fetch_stackoverflow_html(query):
        for answer in find_stackoverflow_answers(raw_html):
            for method in methods:
                for function in method(answer):
                    yield function


def get_function(query, tester, methods=M_ALL):
    for f in build_functions(query, methods):
        if f is not None and apply_tests(f, tester):
            return f
    raise NotImplementedError(
        'No fonction built with query "{}" passed the provided tests'
        .format(query))


def call_stack_overflow(query, *args, **kwargs):
    result = {}

    def just_run_it(f):
        result["out"] = f(*args, **kwargs)
        return True

    get_function(query, just_run_it,
                 [M_SEARCH_FOR_DEF, M_READ_DOCUMENTATION_LINKS])
    return result["out"]
