import datetime

def cache_days(age):
    def cache_decorator(function):
        def wrapper(*args, **kwargs):
            expiry_time = datetime.datetime.utcnow() + datetime.timedelta(age)
            rjd = function(*args, **kwargs)
            rjd['Cache-Control'] = 'public'
            rjd["Expires"] = expiry_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
            return rjd
        return wrapper
    return cache_decorator