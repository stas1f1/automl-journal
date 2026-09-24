#!/usr/bin/env bash
# Выкладка четырёх заданий FEDOT.LLM (полная конфигурация, типы из схемы) на
# Harbor Hub публично. Запуск: bash upload_fedot.sh
set -u
cd "$(dirname "$0")"
for j in fedot-tabred-40min-schema-20260922-141217 \
         fedot-tabred-40min-schema5-20260922-171228 \
         fedot-tabred-40min-schema-sberbank-20260922-175429 \
         fedot-tabred-40min-schema-delivery-20260922-224814; do
  echo "=== $j"
  harbor upload "jobs/$j" --public
done
