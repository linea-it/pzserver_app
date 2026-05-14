#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <product_id> [tail_lines]"
  echo "Example: $0 206 1000"
  exit 1
fi

PRODUCT_ID="$1"
TAIL_LINES="${2:-800}"

if ! [[ "$PRODUCT_ID" =~ ^[0-9]+$ ]]; then
  echo "Error: product_id must be numeric."
  exit 1
fi

echo "== Download Trace =="
echo "product_id=${PRODUCT_ID}"
echo "tail_lines=${TAIL_LINES}"
echo

echo "== Services =="
docker compose ps backend pz-worker rabbitmq || true
RUNNING_BACKEND="$(docker compose ps --status running --services backend 2>/dev/null || true)"
RUNNING_WORKER="$(docker compose ps --status running --services pz-worker 2>/dev/null || true)"
RUNNING_RABBITMQ="$(docker compose ps --status running --services rabbitmq 2>/dev/null || true)"
if [[ "$RUNNING_BACKEND" != "backend" || "$RUNNING_WORKER" != "pz-worker" || "$RUNNING_RABBITMQ" != "rabbitmq" ]]; then
  echo
  echo "backend, pz-worker and rabbitmq must be running for this trace."
  echo "Try: docker compose up -d backend pz-worker rabbitmq"
  exit 2
fi
echo

ARCHIVE_LINE="$(docker compose exec -T backend env PRODUCT_ID="$PRODUCT_ID" python manage.py shell -c "
import os
from core.models import ProductDownloadArchive as A
pid = int(os.environ['PRODUCT_ID'])
a = A.objects.filter(product_id=pid).order_by('-id').first()
if a is None:
    print('NONE')
else:
    print('|'.join([
        str(a.id),
        a.task_id or '',
        a.status or '',
        (a.error_message or '').replace('\\n', ' ')[:400],
        a.created_at.isoformat() if a.created_at else '',
        a.updated_at.isoformat() if a.updated_at else '',
        a.archive_path or '',
        str(a.size or ''),
    ]))
")"

if [[ "$ARCHIVE_LINE" == "NONE" ]]; then
  echo "No ProductDownloadArchive found for product_id=${PRODUCT_ID}."
  exit 0
fi

IFS='|' read -r ARCHIVE_ID TASK_ID STATUS ERROR_MESSAGE CREATED_AT UPDATED_AT ARCHIVE_PATH ARCHIVE_SIZE <<< "$ARCHIVE_LINE"

echo "== Latest Archive =="
echo "archive_id=${ARCHIVE_ID}"
echo "task_id=${TASK_ID:-<empty>}"
echo "status=${STATUS}"
echo "created_at=${CREATED_AT}"
echo "updated_at=${UPDATED_AT}"
echo "archive_path=${ARCHIVE_PATH:-<empty>}"
echo "size=${ARCHIVE_SIZE:-<empty>}"
echo "error_message=${ERROR_MESSAGE:-<empty>}"
echo

echo "== App File Logs (/archive/log/*.log) =="
DJANGO_FILE_LOGS="$(docker compose exec -T backend sh -lc "tail -n ${TAIL_LINES} /archive/log/django.log 2>/dev/null || true")"
TASKS_FILE_LOGS="$(docker compose exec -T backend sh -lc "tail -n ${TAIL_LINES} /archive/log/tasks.log 2>/dev/null || true")"
if command -v rg >/dev/null 2>&1; then
  printf '%s\n' "$DJANGO_FILE_LOGS" | rg -n "download_prepare queued|download_prepare reusing|archive_id=${ARCHIVE_ID}|task_id=${TASK_ID}|product_id=${PRODUCT_ID}" || true
  printf '%s\n' "$TASKS_FILE_LOGS" | rg -n "build_product_download_archive started|build_product_download_archive finished|build_product_download_archive failed|archive_id=${ARCHIVE_ID}|task_id=${TASK_ID}|product_id=${PRODUCT_ID}" || true
else
  printf '%s\n' "$DJANGO_FILE_LOGS" | grep -nE "download_prepare queued|download_prepare reusing|archive_id=${ARCHIVE_ID}|task_id=${TASK_ID}|product_id=${PRODUCT_ID}" || true
  printf '%s\n' "$TASKS_FILE_LOGS" | grep -nE "build_product_download_archive started|build_product_download_archive finished|build_product_download_archive failed|archive_id=${ARCHIVE_ID}|task_id=${TASK_ID}|product_id=${PRODUCT_ID}" || true
fi
echo

echo "== Backend Logs (download_prepare/status) =="
if command -v rg >/dev/null 2>&1; then
  docker compose logs --tail "$TAIL_LINES" backend | rg -n "download_prepare|/download/prepare/|/download/status/|archive_id=${ARCHIVE_ID}|task_id=${TASK_ID}|product_id=${PRODUCT_ID}" || true
else
  docker compose logs --tail "$TAIL_LINES" backend | grep -nE "download_prepare|/download/prepare/|/download/status/|archive_id=${ARCHIVE_ID}|task_id=${TASK_ID}|product_id=${PRODUCT_ID}" || true
fi
echo

echo "== Worker Logs (task lifecycle) =="
if command -v rg >/dev/null 2>&1; then
  docker compose logs --tail "$TAIL_LINES" pz-worker | rg -n "build_product_download_archive started|build_product_download_archive finished|build_product_download_archive failed|archive_id=${ARCHIVE_ID}|task_id=${TASK_ID}|product_id=${PRODUCT_ID}" || true
else
  docker compose logs --tail "$TAIL_LINES" pz-worker | grep -nE "build_product_download_archive started|build_product_download_archive finished|build_product_download_archive failed|archive_id=${ARCHIVE_ID}|task_id=${TASK_ID}|product_id=${PRODUCT_ID}" || true
fi
echo

if [[ -n "${TASK_ID}" ]]; then
  echo "== Celery Inspect (active/reserved/scheduled) =="
  ACTIVE="$(docker compose exec -T pz-worker celery -A pzserver inspect active 2>/dev/null || true)"
  RESERVED="$(docker compose exec -T pz-worker celery -A pzserver inspect reserved 2>/dev/null || true)"
  SCHEDULED="$(docker compose exec -T pz-worker celery -A pzserver inspect scheduled 2>/dev/null || true)"

  if command -v rg >/dev/null 2>&1; then
    printf '%s\n' "$ACTIVE" | rg -n "$TASK_ID" || true
    printf '%s\n' "$RESERVED" | rg -n "$TASK_ID" || true
    printf '%s\n' "$SCHEDULED" | rg -n "$TASK_ID" || true
  else
    printf '%s\n' "$ACTIVE" | grep -n "$TASK_ID" || true
    printf '%s\n' "$RESERVED" | grep -n "$TASK_ID" || true
    printf '%s\n' "$SCHEDULED" | grep -n "$TASK_ID" || true
  fi
  echo
fi

echo "Done."
