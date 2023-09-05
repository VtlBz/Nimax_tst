import csv
import logging
import os

from goods.management.commands import _importcsv_conf as conf
from goods.models import Category, Product, ProductCategory


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

EXIT_COMMANDS_LIST: tuple = ('no', 'n', 'нет', 'н', 'q', 'quit', 'exit',)
CONTINUE_COMMANDS_LIST: tuple = ('yes', 'y', 'да', 'д',)

ERROR_MESSAGE_FILENOTFOUND: str = ('Ошибка обработки запроса. '
                                   'Файла с именем {} не существует '
                                   'в указанной директории.')
ERROR_MESSAGE_CONSTRAINT: str = ('Для корректной обработки импорта '
                                 'имя файла должно соответствовать '
                                 'указанному в таблице соответствия.')


FILE_NAME = 'goods.csv'
APP_NAME = 'goods'
APP_MODELS = ('Category', 'Product')


def confirmation() -> None:
    print('Данный скрипт импортирует данные '
          'из .csv файлов в базу данных проекта.')
    print(f'{FILE_NAME} --> {APP_MODELS}')
    print('Импорт будет произведён в указанном выше порядке')
    print('Проверьте соответствие имён файлов в каталоге '
          'на соответствие указанным выше, прежде чем продолжить.')

    while True:
        q = input('Подтвердить (yes/no)? ') or ''
        if q.lower() in CONTINUE_COMMANDS_LIST:
            break
        if q.lower() in EXIT_COMMANDS_LIST:
            raise SystemExit('Операция отменена пользователем')
        print('Ошибка! Команда не распознана!')
        print('Допустимые значения:')
        print(f'Подтвердить и продолжить - {CONTINUE_COMMANDS_LIST}')
        print(f'Отменить и выйти - {EXIT_COMMANDS_LIST}')


def _get_file_path(folder_path, file_name) -> str:
    for root, dirs, files in os.walk(folder_path):
        if file_name in files:
            return str(os.path.join(root, file_name))
        logger.error(ERROR_MESSAGE_FILENOTFOUND.format(file_name))
        raise SystemExit(ERROR_MESSAGE_CONSTRAINT)


def _process_tables(reader, file_name) -> None:
    next(reader)
    row_count = row_success = 0
    cat_row_success = prod_row_success = 0
    for name, price, categories, is_public, is_archive in reader:
        _category_obj_dict = {
            'name': categories,
        }
        category, is_create = Category.objects.get_or_create(
            **_category_obj_dict
        )
        if is_create:
            cat_row_success += 1
        _product_obj_dict = {
            'name': name,
            'price': price,
            'is_public': int(is_public),
            'is_archive': int(is_archive),
        }
        product, is_create = Product.objects.get_or_create(
            **_product_obj_dict
        )
        if is_create:
            prod_row_success += 1
        _product_category_obj_dict = {
            'product': product,
            'category': category,
        }
        _, is_create = ProductCategory.objects.get_or_create(
            **_product_category_obj_dict
        )
        if is_create:
            row_success += 1
        row_count += 1
    logger.info(f'Конец обработки файла {file_name}, '
                f'обработано строк - {row_count}, '
                f'создано категорий - {cat_row_success}, '
                f'создано продуктов - {prod_row_success}, '
                f'успешно создано связей - {row_success}.')


def run(folder_path) -> None:
    file_path = _get_file_path(folder_path, conf.FILE_NAME)
    logger.info(f'Начало обработки файла {conf.FILE_NAME}')
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=';', quotechar='"')
        _process_tables(reader, conf.FILE_NAME)
