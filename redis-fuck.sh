#!/bin/sh
redis-cli < redis-remove.txt
mv feedreader/media/cache2 feedreader/media/cache_old
rm feedreader/media/cache_old -Rf &
