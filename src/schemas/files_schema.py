from pydantic import BaseModel

# Files Service schemas

class FileItemSchema(BaseModel):
    id: str
    external_id: str
    name: str
    provider: str
    product: str | None = None
    category: str | None = None
    mime_type: str | None = None

    model_config = {
        "extra": "allow"
    }


class FilesListResponseSchema(BaseModel):
    files: list[FileItemSchema]

    model_config = {
        "extra": "allow"
    }