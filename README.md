# 📱 Social Media API

> A **production-ready**, scalable REST API backend for a social media platform — built with Django, Django REST Framework, and JWT Authentication.

---

## ✨ Features at a Glance

| Feature | Details |
|---|---|
| 🔐 **JWT Authentication** | Stateless, secure token-based auth via `djangorestframework-simplejwt` |
| 👤 **User Profiles** | Custom user model with profile management (avatar, bio, name) |
| 📸 **Posts & Reels** | Full CRUD for image posts and video reels |
| 🤝 **Follow System** | Follow/unfollow users with a unique constraint to prevent duplicates |
| 🚀 **Smart Caching** | Per-user, per-page cache keys using Django's cache framework |
| 📄 **Pagination** | Configurable page-size pagination on all list endpoints |
| 🗄️ **Media Handling** | `ImageField` / `FileField` with automatic file serving in development |
| 🛡️ **Role-based Users** | Built-in `MODERATOR` / `USER` roles on the custom User model |

---

## 🏗️ Architecture & Project Structure

```
social_media/
│
├── social_media/          # Project configuration (settings, root URLs)
│   ├── settings.py        # JWT auth, DRF config, media, DB
│   ├── urls.py            # Root URL dispatcher
│   └── pagination.py      # Shared PageNumberPagination class
│
├── authentication/        # User registration, login & profiles
│   ├── models.py          # Custom User + Profile models
│   ├── serializers.py     # Registration, Profile & nested serializers
│   ├── views.py           # RegisterAPI, MyProfileAPI, AllProfileAPI
│   └── urls.py            # /auth/ routes
│
├── core/                  # Cross-app domain logic
│   ├── models.py          # Follow model (follower ↔ following)
│   ├── views.py           # FollowAPI
│   └── urls.py            # /core/ routes
│
├── post/                  # Posts & Reels functionality
│   ├── models.py          # Post, Reel models
│   ├── serializer.py      # PostSerializer, ReelSerializer (nested Profile)
│   ├── views.py           # Feed, MyPostAPI, MyReelAPI with caching
│   ├── cache_key.py       # Deterministic cache key helpers
│   └── urls.py            # /post/ routes
│
└── chat/                  # (Scaffolded) Real-time chat module
```

---

## 🧩 Key Concepts Demonstrated

### 1. 🔐 Custom User Model + JWT Authentication

A custom `AbstractUser` is used so that `mobile_no` and `role` fields can be added without hacking Django's internals. JWT is used for stateless authentication — no sessions, no cookies.

```python
# authentication/models.py
class User(AbstractUser):
    ROLE_CHOICES = [('MODERATOR', 'Moderator'), ('USER', 'User')]
    mobile_no = models.CharField(max_length=15, unique=True)
    role      = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')
```

```python
# social_media/settings.py
AUTH_USER_MODEL = "authentication.User"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}
```

---

### 2. 🔗 OneToOne Profile Pattern

User account data (auth) and public profile data (display name, bio, avatar) are cleanly separated into two models. The `Profile` is created atomically alongside the `User` on registration.

```python
# authentication/models.py
class Profile(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE)
    name        = models.CharField(max_length=100, null=True)
    bio         = models.TextField(null=True)
    profile_pic = models.ImageField(upload_to='pfps/', null=True)
```

```python
# authentication/views.py — atomic creation
with transaction.atomic():
    user = User.objects.create_user(...)
    Profile.objects.create(user=user)
```

---

### 3. 🤝 Follow System with Unique Constraint

The `Follow` model enforces that a user can only follow another user **once**, using Django's `UniqueConstraint` — a database-level guarantee that's far stronger than application-level checks.

```python
# core/models.py
class Follow(models.Model):
    follower   = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='following_relationship')
    following  = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='follower_of')
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'following'], name='unique_follower_following')
        ]
```

---

### 4. 🚀 Smart Per-User Cache with Deterministic Keys

Rather than caching globally (which would leak one user's feed to another), each user's paginated pages are cached under a unique, deterministic key. On write (new post/reel), all cached pages for that user are **invalidated**.

```python
# post/cache_key.py
def post_cache_key(page, user_id):
    return f"post_feed_page:{page}_userid:{user_id}"
```

```python
# post/views.py — Read path (cache hit)
key = post_cache_key(page=page_no, user_id=request.user.id)
cached_data = cache.get(key)
if cached_data is not None:
    return Response(cached_data, status=200)

# ... fetch from DB, paginate, serialize ...
cache.set(key, response.data, timeout=300)   # 5 min TTL

# Write path — invalidate all cached pages on new post
for i in range(1, 21):
    cache.delete(post_cache_key(page=i, user_id=request.user.id))
```

---

### 5. 📄 Global Pagination

A single `PageNumberPagination` class is shared across all list views. Page size is configurable via query param, with a hard ceiling.

```python
# social_media/pagination.py
class GeneralReelAndPostPagination(PageNumberPagination):
    page_size             = 10
    page_size_query_param = 'custom_page_size'
    max_page_size         = 100
```

---

### 6. 🖼️ Nested Serializers

Post and Reel responses embed a nested `ProfileGetSerializer` so the consumer gets author info inline — eliminating a second round-trip.

```python
# post/serializer.py
class PostSerializer(ModelSerializer):
    user = ProfileGetSerializer(read_only=True)  # Nested author info
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['created_on']
```

---

### 7. ⚡ View-level Caching with `cache_page`

Public feed endpoints (post feed, reel feed, all profiles) are cached **at the HTTP response level** for 5 minutes using Django's `cache_page` decorator — perfect for content that's the same for every user.

```python
# post/views.py
class PostFeedAPI(ListAPIView):
    queryset         = Post.objects.select_related('user').all().order_by('-created_on')
    serializer_class = PostSerializer
    pagination_class = GeneralReelAndPostPagination

    @method_decorator(cache_page(60 * 5))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
```

---

### 8. ⚡ N+1 Prevention with `select_related`

Every queryset that touches a foreign key uses `select_related` to JOIN the related table in a single SQL query — preventing the classic N+1 problem.

```python
Post.objects.select_related('user').all()
Profile.objects.select_related('user').all()
Reel.objects.select_related('user__user').filter(user__user=request.user)  # 2 levels deep
```

---

## 🛣️ API Reference

### 🔑 Authentication  (`/auth/`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/register/` | ❌ None | Register a new user |
| `POST` | `/auth/token/` | ❌ None | Obtain JWT access + refresh tokens |
| `POST` | `/auth/token/refresh/` | ❌ None | Refresh an expired access token |
| `GET` / `PATCH` | `/auth/profile/me/` | ✅ JWT | View or update your own profile |
| `GET` | `/auth/profile/all/` | ✅ JWT | Browse all user profiles (paginated, cached) |

### 📸 Posts & Reels  (`/post/`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/post/feed/posts/` | ✅ JWT | Global post feed (cached, paginated) |
| `GET` | `/post/feed/reels/` | ✅ JWT | Global reel feed (cached, paginated) |
| `GET` | `/post/my/posts/` | ✅ JWT | Your own posts (per-user cached) |
| `POST` | `/post/my/posts/` | ✅ JWT | Upload a new post |
| `GET` | `/post/my/reels/` | ✅ JWT | Your own reels (per-user cached) |
| `POST` | `/post/my/reels/` | ✅ JWT | Upload a new reel |

### 🤝 Social  (`/core/`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/core/follow/<profile_id>/` | ✅ JWT | Follow a user by their Profile ID |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repo
git clone <repository-url>
cd social_media

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install django djangorestframework djangorestframework-simplejwt pillow

# 4. Apply database migrations
python manage.py migrate

# 5. (Optional) Create a superuser for Django Admin
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

The API will be available at **`http://127.0.0.1:8000/`**.

---

### Example Workflow

```bash
# 1. Register a user
curl -X POST http://127.0.0.1:8000/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","mobile_no":"9876543210","password":"secret123"}'

# 2. Get JWT tokens
curl -X POST http://127.0.0.1:8000/auth/token/ \
  -d '{"username":"alice","password":"secret123"}' \
  -H "Content-Type: application/json"
# → {"access": "eyJ...", "refresh": "eyJ..."}

# 3. Browse post feed (authenticated)
curl http://127.0.0.1:8000/post/feed/posts/ \
  -H "Authorization: Bearer <access_token>"

# 4. Follow another user (by their Profile ID)
curl -X POST http://127.0.0.1:8000/core/follow/2/ \
  -H "Authorization: Bearer <access_token>"
```

---

## 🔄 Request Flow Diagram

```
Client                     Django                  DB / Cache
  │                           │                        │
  │──POST /auth/register/ ───▶│                        │
  │                           │──INSERT User ─────────▶│
  │                           │──INSERT Profile ───────▶│
  │◀── 201 Created ───────────│                        │
  │                           │                        │
  │──POST /auth/token/ ──────▶│                        │
  │◀── {access, refresh} ─────│                        │
  │                           │                        │
  │──GET /post/my/posts/ ────▶│ Check cache?           │
  │  Authorization: Bearer …  │──cache.get(key) ──────▶│
  │                           │◀── MISS ────────────────│
  │                           │──SELECT posts… ───────▶│
  │                           │──cache.set(key, data) ▶│
  │◀── 200 paginated posts ───│                        │
  │                           │                        │
  │──POST /post/my/posts/ ───▶│ Create post            │
  │                           │──INSERT Post ─────────▶│
  │                           │──cache.delete(keys…) ─▶│  ← invalidate stale cache
  │◀── 201 Created ───────────│                        │
```

---

## 🗺️ Roadmap

- [ ] 💬 **Chat Module** — Real-time messaging (WebSocket via Django Channels)
- [ ] ❤️ **Likes & Comments** — Engagement on Posts and Reels
- [ ] 🔔 **Notifications** — Follow and engagement alerts
- [ ] 🔍 **Search** — Full-text search on profiles and posts
- [ ] 🛑 **Moderation** — MODERATOR role-gated content management endpoints
- [ ] 🐳 **Docker** — Containerized deployment with PostgreSQL + Redis

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5.2 |
| API | Django REST Framework |
| Auth | `djangorestframework-simplejwt` (JWT) |
| Database | SQLite (dev) / PostgreSQL (prod-ready) |
| Caching | Django Cache Framework (in-memory / Redis-ready) |
| Media | Django `FileField` / `ImageField` + Pillow |
| Language | Python 3 |

---

> Built to demonstrate scalable Django patterns: **custom user models**, **JWT stateless auth**, **smart caching strategies**, **N+1 prevention**, and **clean app separation**.
