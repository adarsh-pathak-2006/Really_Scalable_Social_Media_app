from django.core.cache import cache

def post_cache_key(page, user_id):
    return f"post_feed_page:{page}_userid:{user_id}"

def reel_cache_key(page, user_id):
    return f"reel_feed_page:{page}_userid:{user_id}"