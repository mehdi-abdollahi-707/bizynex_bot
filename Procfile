# Render's own deploys are driven by render.yaml (its buildCommand runs
# migrations before start). This Procfile is kept for portability to
# other Procfile-based platforms; Render does not execute the `release`
# phase the way Heroku does, so on Render migrations only run via
# render.yaml's buildCommand.
release: python manage.py migrate --noinput
web: gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker --workers 1 --timeout 60 --bind 0.0.0.0:$PORT
