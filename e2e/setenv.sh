#!/bin/bash

# Invoke "source setenv.sh" to populate environment variables locally

export DJANGO_DATABASE_URL="postgres://postgres:postgres@localhost:5432/django"
export DJANGO_MINIO_STORAGE_ENDPOINT="localhost:9000"
export DJANGO_MINIO_STORAGE_ACCESS_KEY="minioAccessKey"
export DJANGO_MINIO_STORAGE_SECRET_KEY="minioSecretKey"
export DJANGO_STORAGE_BUCKET_NAME="dandi-bucket"
export DJANGO_DANDI_DANDISETS_BUCKET_NAME="dandi-bucket"
export DJANGO_DANDI_DANDISETS_LOG_BUCKET_NAME="dandiapi-dandisets-logs"
export DJANGO_DANDI_DANDISETS_EMBARGO_BUCKET_NAME="dandi-embargo-dandisets"
export DJANGO_DANDI_DANDISETS_EMBARGO_LOG_BUCKET_NAME="dandiapi-embargo-dandisets-logs"
export DJANGO_DANDI_WEB_APP_URL="http://localhost:8085"
export DJANGO_DANDI_API_URL="http://localhost:8000"
export DJANGO_DANDI_JUPYTERHUB_URL="https://hub.dandiarchive.org/"
export DANDI_ALLOW_LOCALHOST_URLS="1"
export VITE_APP_DANDI_API_ROOT="http://localhost:8000/api/"
export VITE_APP_OAUTH_API_ROOT="http://localhost:8000/oauth/"
export VITE_APP_OAUTH_CLIENT_ID="Dk0zosgt1GAAKfN8LT4STJmLJXwMDPbYWYzfNtAl"
export CLIENT_URL="http://localhost:8085"
