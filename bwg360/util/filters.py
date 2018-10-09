

# https://www.zhihu.com/question/24601215
def sizeof_fmt(num, suffix='B'):
    """num unit is MB"""
    if num == 0:
        return 'Unknow'

    try:
        num = float(num)
    except TypeError:
        return 'Unknow'

    # ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']
    for unit in ['Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "{:3.1f}{}{}".format(num, unit, suffix)
        num /= 1024.0
    return "{:3.1f}{}{}".format(num, 'Yi', suffix)


def transform(category):
    if category == 'error':
        return 'danger'
    else:
        return category


def readable(flag):
    if flag:
        return u"是"
    else:
        return u"否"
