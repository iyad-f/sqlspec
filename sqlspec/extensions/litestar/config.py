from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Literal, Optional, Union

from sqlspec.exceptions import ImproperConfigurationError
from sqlspec.extensions.litestar.handlers import (
    autocommit_handler_maker,
    connection_provider_maker,
    lifespan_handler_maker,
    manual_handler_maker,
    pool_provider_maker,
    session_provider_maker,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable
    from contextlib import AbstractAsyncContextManager

    from litestar import Litestar
    from litestar.datastructures.state import State
    from litestar.types import BeforeMessageSendHookHandler, Scope

    from sqlspec.base import AsyncConfigT, DriverT, SyncConfigT
    from sqlspec.typing import ConnectionT, PoolT


CommitMode = Literal["manual", "autocommit", "autocommit_include_redirect"]
DEFAULT_COMMIT_MODE: CommitMode = "manual"
DEFAULT_CONNECTION_KEY = "db_connection"
DEFAULT_POOL_KEY = "db_pool"
DEFAULT_SESSION_KEY = "db_session"


@dataclass
class DatabaseConfig:
    config: "Union[SyncConfigT, AsyncConfigT]" = field()  # type: ignore[valid-type]   # pyright: ignore[reportGeneralTypeIssues]
    connection_key: str = field(default=DEFAULT_CONNECTION_KEY)
    pool_key: str = field(default=DEFAULT_POOL_KEY)
    session_key: str = field(default=DEFAULT_SESSION_KEY)
    commit_mode: "CommitMode" = field(default=DEFAULT_COMMIT_MODE)
    extra_commit_statuses: "Optional[set[int]]" = field(default=None)
    extra_rollback_statuses: "Optional[set[int]]" = field(default=None)
    connection_provider: "Callable[[State,Scope], Awaitable[ConnectionT]]" = field(init=False, repr=False, hash=False)  # pyright: ignore[reportGeneralTypeIssues]
    pool_provider: "Callable[[State,Scope], Awaitable[PoolT]]" = field(init=False, repr=False, hash=False)  # pyright: ignore[reportGeneralTypeIssues]
    session_provider: "Callable[[State,Scope], Awaitable[DriverT]]" = field(init=False, repr=False, hash=False)  # pyright: ignore[reportGeneralTypeIssues]
    before_send_handler: "BeforeMessageSendHookHandler" = field(init=False, repr=False, hash=False)
    lifespan_handler: "Callable[[Litestar], AbstractAsyncContextManager[None]]" = field(
        init=False,
        repr=False,
        hash=False,
    )
    annotation: "type[Union[SyncConfigT, AsyncConfigT]]" = field(init=False, repr=False, hash=False)  # type: ignore[valid-type]   # pyright: ignore[reportGeneralTypeIssues]

    def __post_init__(self) -> None:
        if not self.config.support_connection_pooling and self.pool_key == DEFAULT_POOL_KEY:  # type: ignore[union-attr,unused-ignore]
            """If the database configuration does not support connection pooling, the pool key must be unique.  We just automatically generate a unique identify so it won't conflict with other configs that may get added"""
            self.pool_key = f"_{self.pool_key}_{id(self.config)}"
        if self.commit_mode == "manual":
            self.before_send_handler = manual_handler_maker(connection_scope_key=self.connection_key)
        elif self.commit_mode == "autocommit":
            self.before_send_handler = autocommit_handler_maker(
                commit_on_redirect=False,
                extra_commit_statuses=self.extra_commit_statuses,
                extra_rollback_statuses=self.extra_rollback_statuses,
                connection_scope_key=self.connection_key,
            )
        elif self.commit_mode == "autocommit_include_redirect":
            self.before_send_handler = autocommit_handler_maker(
                commit_on_redirect=True,
                extra_commit_statuses=self.extra_commit_statuses,
                extra_rollback_statuses=self.extra_rollback_statuses,
                connection_scope_key=self.connection_key,
            )
        else:
            msg = f"Invalid commit mode: {self.commit_mode}"  # type: ignore[unreachable]
            raise ImproperConfigurationError(detail=msg)
        self.lifespan_handler = lifespan_handler_maker(config=self.config, pool_key=self.pool_key)
        self.connection_provider = connection_provider_maker(connection_key=self.connection_key, config=self.config)
        self.pool_provider = pool_provider_maker(pool_key=self.pool_key, config=self.config)
        self.session_provider = session_provider_maker(session_key=self.session_key, config=self.config)
