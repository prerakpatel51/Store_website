# Store_website

A Django storefront for Spirits2U. The public site has a home page with searchable location cards and a map, individual store pages, and birthdate verification. Django Admin manages stores, photos, hours, phone numbers, DoorDash links, site text and images, and the age-verification log.

## Run locally

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
DJANGO_DEBUG=1 .venv/bin/python manage.py runserver 127.0.0.1:8000
```

Open http://127.0.0.1:8000/. The admin is at http://127.0.0.1:8000/admin/. Create an admin account with `.venv/bin/python manage.py createsuperuser` if needed.

Store coordinates are entered in Admin. Each store has its own numbered map label connected to its saved point. Stores at the same address may share a point while retaining separate labels and store pages.

Visitors enter their birthdate and answer whether they are 21 or older. A successful home-page check covers store pages during the same session. A direct store-page visit asks for verification. Each attempt is appended to `data/age_verification.jsonl`; superusers can view and clear the file from Admin.

The repository includes the 11 public store locations as a starter fixture. The migration seeds them only when missing, so later admin edits are retained. Local databases, uploaded photos, verification logs, and secrets are excluded from Git. Add store photos and production settings through Admin and environment variables.
