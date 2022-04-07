from datetime import datetime
from os.path import splitext


def get_timestamp_path(
    instance, filename
):  # генерирующей  имена  сохраняемых  в  модели  выгруженных  файлов
    return "%s%s" % (datetime.now().timestamp(), splitext(filename)[1])
