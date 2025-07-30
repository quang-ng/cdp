import gzip
import io
import json
from datetime import datetime

import boto3


class S3BatchUploader:
    def __init__(self, bucket, prefix, threshold=20000, aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None, region_name=None, endpoint_url=None):
        self.bucket = bucket
        self.prefix = prefix
        self.threshold = threshold
        self.buffer = []
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=region_name,
            endpoint_url=endpoint_url
        )

    def add_record(self, record, stream_name):
        """
        Add a record to the buffer for a given stream. When threshold is met, flush to S3.
        """
        if not hasattr(self, 'stream_buffers'):
            self.stream_buffers = {}
        if stream_name not in self.stream_buffers:
            self.stream_buffers[stream_name] = []
        self.stream_buffers[stream_name].append(record)
        if len(self.stream_buffers[stream_name]) >= self.threshold:
            self.flush(stream_name)

    def flush(self, stream_name=None):
        """
        Flush buffer(s) to S3. If stream_name is given, flush only that stream. Otherwise, flush all.
        """
        if not hasattr(self, 'stream_buffers'):
            return
        streams = [stream_name] if stream_name else list(self.stream_buffers.keys())
        for s in streams:
            buf = self.stream_buffers.get(s, [])
            if not buf:
                continue
            now = datetime.now().strftime('%Y%m%dT%H%M%S')
            key = f"{self.prefix}/{s}_{now}.ndjson.gz"
            out = io.BytesIO()
            with gzip.GzipFile(fileobj=out, mode='w') as gz:
                for rec in buf:
                    line = json.dumps(rec) + '\n'
                    gz.write(line.encode('utf-8'))
            out.seek(0)
            self.s3.upload_fileobj(out, self.bucket, key)
            self.stream_buffers[s] = []
