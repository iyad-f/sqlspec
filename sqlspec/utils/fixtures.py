from typing import TYPE_CHECKING, Any, Union

from sqlspec._serialization import decode_json
from sqlspec.exceptions import MissingDependencyError

if TYPE_CHECKING:
    from pathlib import Path

    from anyio import Path as AsyncPath

__all__ = ("open_fixture", "open_fixture_async")


def open_fixture(fixtures_path: "Union[Path, AsyncPath]", fixture_name: str) -> "Any":
    """Loads JSON file with the specified fixture name

    Args:
        fixtures_path: :class:`pathlib.Path` | :class:`anyio.Path` The path to look for fixtures
        fixture_name (str): The fixture name to load.

    Raises:
        FileNotFoundError: Fixtures not found.

    Returns:
        Any: The parsed JSON data
    """
    from pathlib import Path

    fixture = Path(fixtures_path / f"{fixture_name}.json")
    if fixture.exists():
        with fixture.open(mode="r", encoding="utf-8") as f:
            f_data = f.read()
        return decode_json(f_data)
    msg = f"Could not find the {fixture_name} fixture"
    raise FileNotFoundError(msg)


async def open_fixture_async(fixtures_path: "Union[Path, AsyncPath]", fixture_name: str) -> "Any":
    """Loads JSON file with the specified fixture name

    Args:
        fixtures_path: :class:`pathlib.Path` | :class:`anyio.Path` The path to look for fixtures
        fixture_name (str): The fixture name to load.

    Raises:
        FileNotFoundError: Fixtures not found.
        MissingDependencyError: The `anyio` library is required to use this function.

    Returns:
        Any: The parsed JSON data
    """
    try:
        from anyio import Path as AsyncPath
    except ImportError as exc:
        raise MissingDependencyError(package="anyio") from exc

    fixture = AsyncPath(fixtures_path / f"{fixture_name}.json")
    if await fixture.exists():
        async with await fixture.open(mode="r", encoding="utf-8") as f:
            f_data = await f.read()
        return decode_json(f_data)
    msg = f"Could not find the {fixture_name} fixture"
    raise FileNotFoundError(msg)
