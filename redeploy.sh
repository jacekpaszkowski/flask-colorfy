#!/bin/sh
set -eu

# /volume4/docker/flask-colorfy/redeploy.sh
#
# W odroznieniu od spotify-backup, ten kontener ma dzialac CIAGLE (to serwer
# HTTP odpytywany przez Home Assistant), wiec - w odroznieniu od
# spotify-backup/redeploy.sh - od razu go tu startujemy (--restart=unless-stopped,
# przezyje restart NAS-a).

cd /volume4/docker/flask-colorfy

CONTAINER_NAME="flask-colorfy"
IMAGE_NAME="jackthemenace/flask-colorfy"

echo "==> Budowanie nowego obrazu: ${IMAGE_NAME}"
docker build -t "${IMAGE_NAME}" .

echo "==> Resetuje kontener: ${CONTAINER_NAME}"
docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true

docker run -d --name "${CONTAINER_NAME}" \
  -v /etc/localtime:/etc/localtime:ro \
  -p 8766:80 \
  --restart=unless-stopped \
  --cpu-shares=50 \
  "${IMAGE_NAME}:latest"

echo "==> Sprzatanie starych, nieotagowanych warstw obrazu..."
docker image prune -f

echo ""
echo "==> Gotowe:"
docker ps -a --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
