# FastAPI web credentials example

```sh
uv sync
```

## Environment setup

Create an env file and fill in your secret key:

```sh
touch .env.local
```

Create a secret key with `openssl rand -hex 32`

```
SECRET_KEY=<output from openssl rand -hex 32>
```

## Development

```sh
uv run fastapi dev --reload
```

### Add test user

```sh
uv run create-test-user
```

Then log in with

- username `a@b.com`
- password `secret`

at localhost:8000/login

## Production

Set the following environment variables via your hosting platform:

- `APP_ENV=prod`
- `DATABASE_URL`
- `SECRET_KEY` - generate with `openssl rand -hex 32`
- `COOKIE_SECURE=True`

Do **not** commit `.env.local` or create `.env.prod` - secrets should be injected by the platform, not stored in files.
