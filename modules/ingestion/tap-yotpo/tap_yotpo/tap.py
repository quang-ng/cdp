
import requests
import singer
from singer import utils

from modules.ingestion.s3_utils import S3BatchUploader

DEFAULT_API_URL = "https://api.yotpo.com/v1/emails"

CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "app_key": {"type": "string"},
        "secret": {"type": "string"},
        "start_date": {"type": "string", "format": "date-time"}
    },
    "required": ["app_key", "secret", "start_date"]
}

EMAIL_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "email": {"type": "string"},
        "status": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"}
    },
    "required": ["id", "email", "status", "created_at"]
}

def do_discover():
    singer.write_schema("emails", EMAIL_SCHEMA, "id")

def do_sync(config):
    headers = {"Content-Type": "application/json", "X-Yotpo-Token": config.get("yotpo_token", "test-token")}
    params = {
        "app_key": config["app_key"],
        "secret": config["secret"],
        "since": config["start_date"]
    }
    api_url = config.get("api_url", DEFAULT_API_URL)


    # 
    uploader = S3BatchUploader(
        bucket=config.get("s3_bucket", "your-s3-bucket"),
        prefix=config.get("s3_prefix", "yotpo/emails"),
        threshold=config.get("s3_threshold", 20000),
        aws_access_key_id=config.get("aws_access_key_id"),
        aws_secret_access_key=config.get("aws_secret_access_key"),
        aws_session_token=config.get("aws_session_token"),
        region_name=config.get("region_name"),
        endpoint_url=config.get("endpoint_url")
    )
    next_page = 1
    while next_page:
        params["page"] = next_page
        resp = requests.get(api_url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        for email in data.get("emails", []):
            uploader.add_record(email, "emails")
            singer.write_record("emails", email)
        next_page = data.get("next_page")
    uploader.flush("emails")

def main():
    args = utils.parse_args(required_config_keys=["app_key", "secret", "start_date"])
    if args.config.get("discover"):
        do_discover()
    else:
        do_discover()
        do_sync(args.config)

if __name__ == "__main__":
    main()

