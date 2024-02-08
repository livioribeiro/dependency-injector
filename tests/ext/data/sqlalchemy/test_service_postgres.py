import os
from importlib.util import find_spec

import pytest
from sqlalchemy import make_url, text

from selva.configuration.defaults import default_settings
from selva.configuration.settings import Settings
from selva.ext.data.sqlalchemy.service import (
    make_engine_service,
    make_sessionmaker_service,
)

from .test_service import _test_engine_service

POSTGRES_URL = os.getenv("POSTGRES_URL")

pytestmark = [
    pytest.mark.skipif(POSTGRES_URL is None, reason="POSTGRES_URL not defined"),
    pytest.mark.skipif(find_spec("asyncpg") is None, reason="asyncpg not present"),
]

SA_DB_URL = make_url(POSTGRES_URL) if POSTGRES_URL else None


async def test_make_engine_service_with_url():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "default": {
                        "url": POSTGRES_URL,
                    },
                },
            },
        }
    )

    await _test_engine_service(settings)


async def test_make_engine_service_with_url_username_password():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "default": {
                        "url": f"postgresql+asyncpg://{SA_DB_URL.host}:{SA_DB_URL.port}/{SA_DB_URL.database}",
                        "username": SA_DB_URL.username,
                        "password": SA_DB_URL.password,
                    },
                },
            },
        }
    )

    await _test_engine_service(settings)


async def test_make_engine_service_with_url_components():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "default": {
                        "drivername": "postgresql+asyncpg",
                        "host": SA_DB_URL.host,
                        "port": SA_DB_URL.port,
                        "database": SA_DB_URL.database,
                        "username": SA_DB_URL.username,
                        "password": SA_DB_URL.password,
                    },
                },
            },
        }
    )

    await _test_engine_service(settings)


async def test_make_engine_service_with_options():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "default": {
                        "url": POSTGRES_URL,
                        "options": {
                            "echo": True,
                            "echo_pool": True,
                        },
                    },
                },
            },
        }
    )

    engine_service = make_engine_service("default")(settings)
    async for engine in engine_service:
        assert engine.echo is True
        assert engine.pool.echo is True


async def test_make_engine_service_with_execution_options():
    settings = Settings(
        default_settings
        | {
            "data": {
                "sqlalchemy": {
                    "default": {
                        "url": POSTGRES_URL,
                        "options": {
                            "execution_options": {"isolation_level": "READ COMMITTED"},
                        },
                    },
                },
            },
        }
    )

    engine_service = make_engine_service("default")
    engine = await anext(engine_service(settings))
    sessionmaker_service = make_sessionmaker_service("default")
    sessionmaker = await sessionmaker_service(engine)

    async with sessionmaker() as session:
        result = await session.execute(text("select 1"))
        assert result.context.execution_options["isolation_level"] == "READ COMMITTED"
