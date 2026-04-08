from  src.schemas.files_schema import FilesListResponseSchema


async def get_file_id_by_external_id(
        files_client,
        headers: dict,
        external_id: str) -> str:
    response = await files_client.get_files(headers=headers)
    assert response.status_code == 200

    parsed = FilesListResponseSchema.model_validate(response.json())

    for file in parsed.files:
        if file.external_id == external_id:
            return file.id
    raise AssertionError(f"File with external_id {external_id} not found")