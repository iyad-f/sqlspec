from __future__ import annotations

from typing import TYPE_CHECKING

from tools.sphinx_ext import changelog, missing_references

if TYPE_CHECKING:
    from sphinx.application import Sphinx


def setup(app: Sphinx) -> dict[str, bool]:
    ext_config = {}
    ext_config.update(missing_references.setup(app))  # pyright: ignore[reportUnknownMemberType]
    ext_config.update(changelog.setup(app))  # type: ignore[arg-type]  # pyright: ignore[reportUnknownMemberType]

    return ext_config  # pyright: ignore[reportUnknownVariableType]
