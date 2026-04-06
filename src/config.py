from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    base_url: str

    admin_identity: str | None = None
    admin_password: str | None = None
    admin_org: str | None = None

    user_identity: str | None = None
    user_password: str | None = None
    user_org: str | None = None

    super_admin_identity: str | None = None
    super_admin_password: str | None = None
    super_admin_org: str | None = None


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding = "utf-8",
        extra="ignore"
    )

settings = Settings()