from minio import Minio

from app.core.config import (
    MINIO_ACCESS_KEY,
    MINIO_BUCKET,
    MINIO_ENDPOINT,
    MINIO_SECRET_KEY,
)


minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
)


def get_minio_client():
    return minio_client


def init_minio_bucket():
    if not minio_client.bucket_exists(MINIO_BUCKET):
        minio_client.make_bucket(MINIO_BUCKET)


def minio_put_object(object_name, file_content):
    file_size = len(file_content)
    minio_client.put_object(MINIO_BUCKET, object_name, file_content, file_size)
    object_url = f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{object_name}"
    return object_url
