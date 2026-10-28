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
2. Configure PostgreSQL connection URLs and a random `SECRET_KEY` in `.env.local` or the process environment. Use the pooled `DATABASE_URL` for app traffic and the direct `DATABASE_URL_UNPOOLED` for migrations.
3. Install dependencies:
   `python3 -m pip install -r requirements.txt`
4. Run migrations:
   `NEON_USE_UNPOOLED_DATABASE_URL=1 python3 manage.py migrate`
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

This repository includes a Render Blueprint in `render.yaml`. The web service uses Neon PostgreSQL and Neon Object Storage for durable media, with WhiteNoise for static assets. Render free web services sleep after periods without traffic, so the first request after idle can take a little longer.

1. Push this project to a GitHub repository. Do not commit `.env`, `.env.local`, or database credentials.
2. In Render, choose **New + → Blueprint**, connect the GitHub repository, and apply the `render.yaml` blueprint.
3. Keep `DEBUG=False`; Render generates `SECRET_KEY`. Provide the pooled PostgreSQL URL as `DATABASE_URL` and the direct PostgreSQL URL as `DATABASE_URL_UNPOOLED` in the Render environment. Never commit either URL.
4. In Neon, create a new empty project in a region supporting Object Storage, create a private bucket named `digital-business-id-media`, and create a storage credential with read/write access. Add its endpoint, region, access key ID, and secret access key to the matching Render environment variables. Never commit or share the credential values.
5. Wait for the first deployment. The start command applies database migrations over the direct connection and starts Gunicorn; static files are collected during the build.
6. QR links default to Render's assigned HTTPS hostname. Set `SITE_URL` in the service environment to your canonical HTTPS URL if using a custom domain, then redeploy.
7. Open the service Shell and run `python manage.py createsuperuser` to create your own administrator account. Do not use example/default credentials.
8. The new database is empty, so no local records are imported. If profiles are later created before a valid `SITE_URL` is configured, run `python manage.py generate_profile_qr_codes --regenerate-generated` after setting it.

For local development, `SITE_URL` defaults to `http://127.0.0.1:8000` and uploads use the local filesystem. Production file URLs use signed requests to the private Neon bucket; configure the bucket and all `AWS_*` environment variables before deploying. Neon Object Storage currently requires one of these regions: `aws-us-east-2`, `aws-us-east-1`, `aws-eu-central-1`, or `aws-ap-southeast-1`.

## Run tests

Use the test settings module to run tests against an isolated, in-memory SQLite database:

```sh
python3 manage.py test --settings=digital_identity.test_settings
```

The test settings use an isolated in-memory SQLite database and do not modify your PostgreSQL database. Object storage remains disabled in tests unless explicitly configured.

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
