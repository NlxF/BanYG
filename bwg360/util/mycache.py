"""
    custom cache class
"""
from . import (string_types, integer_types, Singleton,
               size_free_download, anonymous_free_download,
               sequence_free_download_prefix, sequence_free_download_step,
               sequence_free_download_toast, over_total_free_download_toast,
               visitor_no_free_download_toast, search_prefix, TimeConver, free_download_one_day)
try:
    import redis
except ImportError:
    raise RuntimeError('no redis module found')
try:
    import cPickle as pickle
except ImportError:  # pragma: no cover
    import pickle


class MyRedisCache(metaclass=Singleton):
    def __init__(self, host='localhost', port=6379, password=None,
                 db=0, default_timeout=300, key_prefix='MyCache:', **kwargs):

        if host is None:
            raise ValueError('host parameter may not be None')
        if not isinstance(host, string_types):
            raise ValueError('host parameter must be string')
        if kwargs.get('decode_responses', None):
            raise ValueError('decode_responses is not supported')

        self._client = redis.StrictRedis(host, port=port, password=password, db=db, decode_responses=False, **kwargs)

        self.default_timeout = default_timeout
        self.key_prefix = key_prefix

    @staticmethod
    def getInstance():
        """static access method, use default setting"""
        return MyRedisCache()

    def _key(self, key):
        return "{}{}".format(self.key_prefix, key)

    def _normalize_timeout(self, _timeout):
        if _timeout == 0:
            timeout = -1
        elif _timeout < 0:
            timeout = self.default_timeout
        else:
            timeout = _timeout
        return timeout

    def _set_expire(self, key):
        return self._client.expire(self._key(key), self.default_timeout)

    def dump_object(self, value):
        t = type(value)
        if t in integer_types:
            return str(value).encode('ascii')
        return b'!' + pickle.dumps(value)

    def load_object(self, value):
        if value is None:
            return None
        if value.startswith(b'!'):
            try:
                return pickle.loads(value[1:])
            except pickle.PickleError:
                return None
        try:
            return int(value)
        except ValueError:
            return value

    def get(self, key, auto_expire=False):
        """
            if auto_expire =True, it will re-expire time
        """
        value = self.load_object(self._client.get(self._key(key)))
        if auto_expire and value:
            self._set_expire(key)
        return value

    def set(self, key, value, timeout=-1):
        """
            timeout =0, set value no expire;
            timeout <0, set value expire use default time;
            timeout >0, set value expire use Specified time
        """
        timeout = self._normalize_timeout(timeout)
        dump = self.dump_object(value)
        if timeout == -1:
            self._client.set(name=self._key(key), value=dump)
        else:
            self._client.setex(name=self._key(key), value=dump, time=timeout)

    def delete(self, key):
        return self._client.delete(self._key(key))

    def clear(self):
        status = False
        if self.key_prefix:
            keys = self._client.keys(self._key('*'))
            if keys:
                status = self._client.delete(*keys)
        else:
            status = self._client.flushdb()
        return status

    def exists(self, key):
        return self._client.exists(self._key(key))

    def ttl(self, key):
        return self._client.ttl(name=self._key(key))

    def plus(self, key, amount=1):
        self._client.incrby(name=self._key(key), amount=amount)

    def sync_minus(self, key, amount):
        num = 10                                    # 尝试10次
        with self._client.pipeline() as pipe:
            while num > 0:
                try:
                    _key = self._key(key)
                    pipe.watch(_key)
                    pipe.multi()
                    self._client.decr(_key, int(amount)+1)     # 向上取整
                    pipe.execute()
                    break
                except redis.WatchError:
                    num -= 1
                    print("sync failed, try again:%d" % (10 - num))
                    continue

        return num > 0

    def sync_set(self, key, amount):
        num = 10  # 尝试10次
        with self._client.pipeline() as pipe:
            while num > 0:
                try:
                    _key = self._key(key)
                    pipe.watch(_key)
                    pipe.multi()
                    self._client.set(_key, amount)
                    pipe.execute()
                    break
                except redis.WatchError:
                    num -= 1
                    print("sync failed, try again:%d" % (10 - num))
                    continue

        return num > 0


def get_init_free_download_size():
    """返回初始的免费下载量, MB为单位"""
    return free_download_one_day


def get_free_download_size():
    """返回当天还剩余的免费下载余量"""
    amount = MyRedisCache.getInstance().get(size_free_download)
    return amount if amount > 0 else 0


def set_free_download_size(amount):
    """设置当天的免费下载量"""
    amount = 0 if amount < 0 else amount
    MyRedisCache.getInstance().sync_set(size_free_download, amount)


def minus_free_download_size(amount):
    """减免费下载余量"""
    if amount <= 0:
        return

    MyRedisCache.getInstance().sync_minus(size_free_download, amount)


def is_anonymous_has_download(fp, ip):
    """游客是否已下载"""
    msg = None
    toast = visitor_no_free_download_toast
    if fp and isinstance(fp, string_types):
        flag_key_fp = "{}:{}".format(anonymous_free_download, fp)
        fp_rt = MyRedisCache.getInstance().get(flag_key_fp)
        msg = toast if fp_rt else None
    if ip and isinstance(ip, string_types):
        flag_key_ip = "{}:{}".format(anonymous_free_download, ip)
        ip_rt = MyRedisCache.getInstance().get(flag_key_ip)
        msg = toast if ip_rt else None
    return msg


def set_anonymous_download_flag(fp, ip):
    """设置游客已下载"""
    now = TimeConver.asia_time_now()
    seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
    day_seconds = 86400
    if fp and isinstance(fp, string_types):
        flag_key_fp = "{}:{}".format(anonymous_free_download, fp)
        MyRedisCache.getInstance().set(flag_key_fp, 1, int(day_seconds - seconds_since_midnight))
    if ip and isinstance(ip, string_types):
        flag_key_ip = "{}:{}".format(anonymous_free_download, ip)
        MyRedisCache.getInstance().set(flag_key_ip, 1, int(day_seconds - seconds_since_midnight))


def _read_idx(num):
    length = len(sequence_free_download_step)
    return num if num < length else length-1


def is_sequence_free_download(username):
    """连续下载检查"""
    flag_key = "{}:{}".format(sequence_free_download_prefix, username)
    num = MyRedisCache.getInstance().get(flag_key)
    num = 0 if num is None else num
    msg = sequence_free_download_toast[0]
    if num > 0:
        num_key = "{}:{}:{}".format(sequence_free_download_prefix, username, num)
        exist = MyRedisCache.getInstance().get(num_key)
        if exist is not None:                                                               # 还在下载等待期内
            real_idx = _read_idx(num)
            msg = sequence_free_download_toast[real_idx].format(MyRedisCache.getInstance().ttl(num_key)//60 + 1)
        else:
            num = 0                                                                         # 下载记录已超时，可以继续下载
    return num, msg


def set_free_download_sequence_flag(username):
    """一天内free下载的次数记录"""
    flag_key = "{}:{}".format(sequence_free_download_prefix, username)
    num = MyRedisCache.getInstance().get(flag_key)
    num = 1 if num is None else num + 1
    if num == 1:
        now = TimeConver.asia_time_now()
        seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        day_seconds = 86400
        MyRedisCache.getInstance().set(flag_key, num, int(day_seconds - seconds_since_midnight))   # 一天内的free下载次数
    else:
        MyRedisCache.getInstance().plus(flag_key, 1)                                          # 更新下载次数

    num_key = "{}:{}:{}".format(sequence_free_download_prefix, username, num)
    real_idx = _read_idx(num)
    MyRedisCache.getInstance().set(num_key, num, sequence_free_download_step[real_idx] * 60)  # 第num次下载后的记录超时设置


def set_free_download_flag(user_info):
    current_user, fp, ip = user_info
    if current_user is None or current_user.is_anonymous:
        set_anonymous_download_flag(fp, ip)
    elif current_user.brick <= 0:
        set_free_download_sequence_flag(current_user.username)


def check_anonymous(fp, ip):
    # 游客下载校验
    msg = is_anonymous_has_download(fp, ip)
    if msg is not None:
        return msg

    # 免费下载余额检查
    if get_free_download_size() <= 0:
        return over_total_free_download_toast

    return msg


def check_free_user(username):
    # 免费下载次数校验
    num, msg = is_sequence_free_download(username)
    if num > 0:
        return num, msg

    # 免费下载余额检查
    if get_free_download_size() <= 0:
        return 1, over_total_free_download_toast

    return num, msg


def get_file_size_of_format_id(file_url, format_id):
    # 由url和format_id获取缓存的video大小
    redis_cache = MyRedisCache.getInstance()
    details = redis_cache.get("{}:{}".format(search_prefix, file_url))      # 从缓存中取ulr对应的info
    for d in details:
        if d['file_format_id'] == str(format_id):
            return d.get('file_size', 0)
    else:
        return -1


def main():
    import time
    import multiprocessing as mp

    def worker(key, amount):
        cache = MyRedisCache.getInstance()
        print('Process minus:{}--redisCache:{}'.format(mp.current_process(), cache))
        for j in range(1000):
            if cache.sync_minus(key, amount):
                # print('success minus :%d' % amount)
                pass
            else:
                print('fail minus :%d' % amount)

    def reset(key, amount):
        cache = MyRedisCache.getInstance()
        print('Process set:{}--redisCache:{}'.format(mp.current_process(), cache))
        time.sleep(0.3)
        print("before set value is:{}".format(cache.get(key)))
        cache.sync_set(key, amount)

    totally = 10000
    MyRedisCache.getInstance().set('k1', totally)

    _key = 'k1'
    record = []
    for i in range(11):
        process = mp.Process(target=worker, args=(_key, 1))
        process.start()
        record.append(process)
        if i == 5:
            process2 = mp.Process(target=reset, args=(_key, totally))
            process2.start()
            record.append(process2)

    for process in record:
        process.join()

    print("Finally value is:%s" % MyRedisCache.getInstance().get('k1'))


if __name__ == '__main__':
    # test redis sync write and read
    main()
