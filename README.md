# FastAPI web credentials example

```sh
uv sync
```

## Environment setup

Copy the example env file and fill in your secret key:

```sh
cp .env.example .env.local
openssl rand -hex 32  # paste the output as SECRET_KEY in .env.local
```

## Development

```sh
uv run fastapi dev --reload
```

### Add test user

```sh
uv run python scripts/add_test_user.py
```

Then log in with

- username `a@b.com`
- password `secret`

at localhost:8000/login

## Production

Set the following environment variables via your hosting platform:

- `APP_ENV=prod`
- `SECRET_KEY` - generate with `openssl rand -hex 32`
- `COOKIE_SECURE=True`

Do **not** commit `.env.local` or create `.env.prod` - secrets should be injected by the platform, not stored in files.
