# Digital Identity & Smart Profile Management Platform

This project is a Django-based digital identity platform for managing administrator-controlled client records, digital business cards, student IDs, company profiles, and public-facing secure profile pages.

## Features
- Custom administrator authentication model
- Role-based access control for super/admin roles
- Public profile pages with active-only visibility
- Per-profile Ocean, Sunset, Forest, Royal, Lavender, Rose, Slate, and Sand color themes stored in the database
- Optional Google Maps location links on public profiles
- Optional profile introduction video uploads (MP4, WebM, or OGV; 50 MB maximum)
- QR code and vCard contact generation
- Dashboard for tracking clients and profiles
- REST API with JWT admin authentication
- Mobile-friendly HTML/CSS/JavaScript frontend

## Run locally
1. Change into the project folder.
2. Configure a Neon pooled connection as `DATABASE_URL` and a random `SECRET_KEY` in `.env.local` or the process environment. See [Connect a Neon PostgreSQL database](#connect-a-neon-postgresql-database).
3. Install dependencies:
   `python3 -m pip install -r requirements.txt`
4. Run migrations:
   `python3 manage.py migrate`
5. Create a superuser:
   `python3 manage.py createsuperuser`
6. Start the local development server with Django's static and media serving enabled:
   `DEBUG=True python3 manage.py runserver`

`DEBUG` defaults to `False` for safety. Do not enable it in production; production deployments should collect static assets and serve uploaded media through the deployment's media server or storage service.

Generate a local secret key with:

```sh
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Put the generated value in `.env.local` as `SECRET_KEY=...`; never commit it.

## Deploy free on Render

This repository includes a Render Blueprint in `render.yaml`. The free web service uses Neon for PostgreSQL and WhiteNoise for static assets. Render free web services sleep after periods without traffic, so the first request after idle can take a little longer. Their filesystem is ephemeral: uploaded profile photos, organization logos, videos, and QR images are not durable across redeploys or service replacement. Use durable object storage before relying on uploaded media in production.

1. Push this project to a GitHub repository. Do not commit `.env`, `.env.local`, or database credentials.
2. In Render, choose **New + → Blueprint**, connect the GitHub repository, and apply the `render.yaml` blueprint.
3. In the Render service environment settings, provide the Neon pooled connection as `DATABASE_URL` and the direct connection as `DATABASE_URL_UNPOOLED`. Keep `DEBUG=False`; Render generates `SECRET_KEY`.
4. Wait for the first deployment. The start command applies database migrations over the direct connection and starts Gunicorn; static files are collected during the build.
5. After Render assigns the service URL, set `SITE_URL` in its environment settings to that public HTTPS URL and redeploy.
6. Open the service Shell and run `python manage.py createsuperuser` to create your own administrator account. Do not use example/default credentials.
7. If profiles already exist, run `python manage.py generate_profile_qr_codes --regenerate-generated` in the service Shell after setting `SITE_URL`.

For a custom domain, add it in Render and update `SITE_URL` to that HTTPS URL. Uploaded media will still need durable external storage.

## Run tests

Use the test settings module to run tests against an isolated, in-memory SQLite database, regardless of any Neon `DATABASE_URL` configured in `.env`, `.env.local`, or the environment:

```sh
python3 manage.py test --settings=digital_identity.test_settings
```

The regular settings require a Neon PostgreSQL URL and fail at startup if it is missing. Running tests with regular settings creates a PostgreSQL test database named `test_<configured database name>` (for example, `test_neondb`). PostgreSQL-backed tests require permission to create and drop that test database, and no other sessions may still be connected when Django tears it down. The explicit SQLite test settings use an isolated in-memory database and avoid creating, modifying, or dropping any Neon database.

## Connect a Neon PostgreSQL database
The Neon CLI links the project and writes pooled `DATABASE_URL` and direct `DATABASE_URL_UNPOOLED` values to `.env.local` (or `.env` if that file already exists). Django loads `.env` first when present, otherwise `.env.local`. Both files are excluded from Git.

Use the pooled `DATABASE_URL` for normal application traffic. Run schema migrations over the direct connection:

```sh
NEON_USE_UNPOOLED_DATABASE_URL=1 python3 manage.py migrate
```

For a hosted deployment, configure `DATABASE_URL` (pooled) and `DATABASE_URL_UNPOOLED` (direct) as secret environment variables instead of committing either connection string. The application does not fall back to a local SQLite database when `DATABASE_URL` is missing.

Collect static assets as part of each deployment so pages can load their CSS and JavaScript when `DEBUG=False`:

```sh
python3 manage.py collectstatic --noinput
```

WhiteNoise serves the collected assets from `STATIC_ROOT`.

Set `SITE_URL` to the public base URL (for example, `https://your-domain.example`) before creating profiles so generated QR codes link to the correct site. It must be an absolute HTTP(S) URL without credentials, a query string, or a fragment. Profiles created while `SITE_URL` is unavailable are left without a QR code and logged; set the URL and run `python3 manage.py generate_profile_qr_codes` to backfill them.

Each digital profile also has an immutable, random UUID URL at `/item/<uuid>/`. Generated QR codes point to this URL rather than a name-based slug, which makes IDs much harder to enumerate; it does not make a public profile private. After deploying the UUID migration, refresh previously generated QR images with:

```sh
python3 manage.py migrate
python3 manage.py generate_profile_qr_codes --regenerate-generated
```

The migration records which public URL each generated QR encodes. The backfill command creates missing codes, repairs missing generated image files, and refreshes app-generated codes if `SITE_URL` changed. It leaves manually uploaded QR images unchanged. Generated PNGs are stored through Django's media storage and served from their saved URL, avoiding QR generation on every page request.

Public profiles can be downloaded as single-sided, print-ready 3.5 × 2 inch PDF cards. ReportLab is installed with the Python requirements; no system PDF tools are required.

## Useful endpoints
- `/` — public landing page
- `/dashboard/` — administrator dashboard
- `/api/admin/login/` — JWT admin login
- `/id/<slug>/` — public profile page
- `/api/public/profile/<slug>/vcard/` — download a public profile's phone contact card
