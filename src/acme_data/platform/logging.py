"""JSON logs with task-local tenant attribution and explicit structured fields."""

import json
import logging

from acme_data.platform.tenancy import tenant_id


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        data = {"level": record.levelname, "logger": record.name, "message": record.getMessage(),
                "tenant_id": tenant_id.get(), "fields": getattr(record, "fields", {})}
        if record.exc_info:
            data["exception"] = self.formatException(record.exc_info)
        return json.dumps(data, sort_keys=True, default=str)


def configure() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
