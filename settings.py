from pydantic import BaseSettings, Field


class XpublishSettings(BaseSettings):
    user_agent: str = Field(
        "xpublish-osn", description="User agent to use for any queries"
    )
    development: bool = Field(
        False, description="Is the server in a development environment"
    )
    host: str = Field("0.0.0.0", description="Host IP to respond to")
    port: int = Field(9005, description="Port for the server to respond to")
    log_level: str = Field("debug", description="Default logging level")
    proxied: bool = Field(True, description="Is the server operating behind a proxy")


settings = XpublishSettings()
