#!/bin/bash

echo "Введите версию релиза: "
read VERSION

ARCHIVE_NAME="scripts/v${VERSION}.zip"
PROJECT_DIR=$(dirname $(dirname $(realpath $0)))

INCLUDE_ITEMS=(
    "src"
    "README.md"
    "LICENSE"
    "requirements.txt"
    "Dockerfile"
    ".dockerignore"
    "config.yaml"
)

cd $PROJECT_DIR

zip -r $ARCHIVE_NAME "${INCLUDE_ITEMS[@]}"
echo "Архив создан: $ARCHIVE_NAME"