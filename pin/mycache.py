from django.core.cache import cache

def caching(queryset, name, ttl=300):
	query_cache = cache.get(name)
	if query_cache:
		return query_cache

	q = queryset._clone()
	cache.set(name, q, ttl)
	return q

