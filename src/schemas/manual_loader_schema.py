from pydantic import BaseModel


class UploadManualFileResponseSchema(BaseModel):
    message: str
    external_id: str

    model_config = {
        "extra": "allow"
    }