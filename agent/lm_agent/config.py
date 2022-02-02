import logging
import sys
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import AnyHttpUrl, BaseSettings, Field
from pydantic.error_wrappers import ValidationError

logger = logging.getLogger("lm_agent.config")


DEFAULT_DOTENV_PATH = Path("/etc/default/license-manager-agent")
PRODUCT_FEATURE_RX = r"^.+?\..+$"
ENCODING = "UTF8"
TOOL_TIMEOUT = 6  # seconds


class LogLevelEnum(str, Enum):
    """
    Log level name enforcement
    """

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DeployEnvEnum(str, Enum):
    """
    Describes the environment where the app is currently deployed.
    """

    PROD = "PROD"
    STAGING = "STAGING"
    LOCAL = "LOCAL"


_DEFAULT_BIN_PATH = Path(__file__).parent.parent / "bin"


class Settings(BaseSettings):
    """
    App config.

    If you are setting these in the environment, you must prefix "LM2_AGENT_", e.g.
    LM2_AGENT_LOG_LEVEL=DEBUG
    """

    DEPLOY_ENV: Optional[DeployEnvEnum] = DeployEnvEnum.LOCAL

    # base url of an endpoint serving the licensemanager2 backend
    BACKEND_BASE_URL: AnyHttpUrl = Field("http://127.0.0.1:8000")

    # location of the log directory
    LOG_BASE_DIR: Optional[str]

    # path to the license server features config file
    LICENSE_SERVER_FEATURES_CONFIG_PATH: Optional[str]

    # path to the binary for lmutil (needed for FlexLM licenses)
    LMUTIL_PATH: Path = _DEFAULT_BIN_PATH

    # path to the binary for rlmutil (needed for RLM licenses)
    RLMUTIL_PATH: Path = _DEFAULT_BIN_PATH

    # debug mode turns on certain dangerous operations
    DEBUG: bool = False

    # sentry specific settings
    SENTRY_DSN: Optional[str] = None
    SENTRY_SAMPLE_RATE: Optional[float] = Field(1.0, gt=0.0, le=1.0)

    # log level
    LOG_LEVEL: LogLevelEnum = LogLevelEnum.INFO

    # Auth0 config for machine-to-machine security
    AUTH0_DOMAIN: str
    AUTH0_AUDIENCE: str
    AUTH0_CLIENT_ID: str
    AUTH0_CLIENT_SECRET: str

    class Config:
        env_prefix = "LM2_AGENT_"
        if DEFAULT_DOTENV_PATH.is_file():
            env_file = DEFAULT_DOTENV_PATH
        else:
            env_file = Path(".env")


def init_settings() -> Settings:
    """
    Build SETTINGS, and offer a way to gracefully fail if required settings cannot be loaded

    TODO: Determine if this is true. If Settings is missing a required field, it should throw
          an exception that causes the uvicorn process to exit gracefully (with an error code)
    """
    try:
        return Settings()
    except ValidationError as e:
        logger.error(f"Failed to load settings: {str(e)}")
        # neither fastapi nor uvicorn appear to offer a way to do a graceful
        # shutdown as of now, so this is what we've got.
        sys.exit(1)


settings = init_settings()
