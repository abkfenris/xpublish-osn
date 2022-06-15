from typing import Optional

import httpx
from pydantic import BaseSettings, Field, HttpUrl


erddaps_servers_url = "https://raw.githubusercontent.com/IrishMarineInstitute/awesome-erddap/master/erddaps.json"


def get_all_erddap_servers():
    """ If ERDDAP servers aren't specified, load servers from Awesome ERDDAP """
    r = httpx.get(erddaps_servers_url)
    data = r.json()

    servers = {}

    for server in data:
        if server["public"]:
            servers[server["short_name"]] = server["url"]

    return servers


class XpublishSettings(BaseSettings):

    erddap_servers: dict[str, HttpUrl] = Field(
        default_factory=get_all_erddap_servers,
        description="""
        ERDDAP server name and URL pairs in JSON mapping.
        URLs are expected to specify the erddap suffix e.g.: http://neracoos.org/erddap/
        If no servers are specified, the list of servers from https://github.com/IrishMarineInstitute/awesome-erddap are used
        """,
    )
    user_agent: str = Field(
        "xpublish-erddap", description="User agent to use for any queries"
    )
    development: bool = Field(
        False, description="Is the server in a development environment"
    )
    host: str = Field("0.0.0.0", description="Host IP to respond to")
    port: int = Field(9005, description="Port for the server to respond to")
    log_level: str = Field("debug", description="Default logging level")
    proxied: bool = Field(True, description="Is the server operating behind a proxy")

    sentry_dsn: Optional[str] = Field(
        None, description="Optional Sentry DSN for error reporting"
    )
    sentry_sample_rate: float = Field(0.1, description="Sentry trace sample rate")

    def __init__(self) -> None:
        super().__init__()

        self.clean_server_ids()

    def clean_server_ids(self):
        """ Replace the ERDDAP server IDs with ones that can be part of a dataset_id slug """
        servers = {}

        for name, url in self.erddap_servers.items():
            name = name.replace("-", "_").replace(" ", "_")
            servers[name] = url

        self.erddap_servers = servers


settings = XpublishSettings()
