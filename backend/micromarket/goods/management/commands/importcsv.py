from django.core.management.base import BaseCommand

from goods.management.commands import _importcsv_conf as conf, _importcsv_main


class Command(BaseCommand):
    help = 'Создание объектов модели из файла по указанному пути.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-p', '--path',
            dest='path',
            type=str,
            help='Определяет путь к папке с импортируемыми файлами',
            default=conf.DEFAULT_PATH
        )

    def handle(self, *args, **options):
        _importcsv_main.confirmation()
        _importcsv_main.run(options['path'])
        print('Импорт завершён!')
