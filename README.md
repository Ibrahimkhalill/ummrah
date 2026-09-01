# Ummrah — Travel Platform API

A Django REST API for an Umrah travel platform: city and location guides, bookable services, licensed guide profiles, in-app chat, payments and push notifications.

## API surface

Mounted in `moha/urls.py`:

| Prefix | App | Covers |
|---|---|---|
| `/api/auth/` | `authentications` | Registration, login, OTP, user and guide profiles |
| `/api/mainapp/` | `mainapp` | Cities, locations, services, blogs, transactions, help & support |
| `/api/chat/` | `chat` | Chat history and messages |
| `/api/notification/` | `notifications` | Firebase tokens and notifications |
| `/api/payment/` | `payment` | Payment handling |
| `/ckeditor5/` | — | Rich-text editor uploads |
| `/admin/` | — | Django admin |

## Data model

| App | Models |
|---|---|
| `authentications` | `CustomUser` (custom `AbstractUser`), `OTP`, `UserProfile`, `Language`, `GuideProfile` |
| `mainapp` | `MainCity`, `Location`, `Services`, `Transactions`, `HelpSupport`, `Blog` |
| `chat` | `ChatHistory`, `ChatMessage` |
| `notifications` | `FirebaseToken`, `Notification` |

## Stack

- Django + Django REST Framework
- **Daphne / Channels** — ASGI, for real-time chat
- **Cloudinary** (`cloudinary_storage`) — media storage
- **django-ckeditor-5** — rich text for blog content
- **django-cors-headers** — cross-origin access for the client apps
- Firebase Cloud Messaging for push notifications

## Getting started

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

A `Pipfile` is also checked in if you prefer `pipenv install`.

You will need to configure Cloudinary credentials, the Django `SECRET_KEY`, and Firebase server credentials before the media, auth and notification paths work.

## Deployment

`render.yml` defines a [Render](https://render.com) web service:

```
gunicorn moha.wsgi --bind 0.0.0.0:$PORT
```

with `DJANGO_SETTINGS_MODULE=moha.settings` and a generated `SECRET_KEY`.

## Notes

- **The settings package is `moha/`, not `mainapp/`.** `mainapp/` is a regular app. Use `moha.settings` / `moha.wsgi` when configuring anything.
- Because Channels and Daphne are installed, run the project under ASGI (`moha.asgi`) in production, not plain WSGI, if you need chat to work in real time.
- `db.sqlite3`, `scheduler.log` and the `media/` folder are committed to the repository. Consider adding them to `.gitignore` and rotating any credentials that were ever committed.
