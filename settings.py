import httpx
from pydantic import BaseSettings, Field, HttpUrl


erddaps_servers_url = "https://raw.githubusercontent.com/IrishMarineInstitute/awesome-erddap/master/erddaps.json"


def get_all_erddap_servers():
    r = httpx.get(erddaps_servers_url)
    data = r.json()

    servers = {}

    for server in data:
        if server["public"]:
            # short_name = server["short_name"].replace("-", "_").replace(" ", "_")
            short_name = server["short_name"]

            servers[short_name] = server["url"]

    return servers


class XpublishSettings(BaseSettings):
    erddap_servers: dict[str, HttpUrl] = Field(default_factory=get_all_erddap_servers)
    user_agent: str = "xpublish-erddap"
    development: bool = False
    host: str = "0.0.0.0"
    port: int = 9005
    log_level: str = "debug"

    def __init__(self) -> None:
        super().__init__()

        servers = {}

        for name, url in self.erddap_servers.items():
            name = name.replace("-", "_").replace(" ", "_")
            servers[name] = url

        self.erddap_servers = servers


settings = XpublishSettings()
