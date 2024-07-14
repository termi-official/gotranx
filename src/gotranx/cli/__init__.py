from __future__ import annotations
import typing
from pathlib import Path
import warnings

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated  # type: ignore

import typer

from ..schemes import Scheme
from ..codegen import PythonFormatter, CFormatter
from . import gotran2c, gotran2py

app = typer.Typer()


def version_callback(show_version: bool):
    """Prints version information."""
    if show_version:
        from .. import __version__, __program_name__

        typer.echo(f"{__program_name__} {__version__}")
        raise typer.Exit()


def license_callback(show_license: bool):
    """Prints license information."""
    if show_license:
        from .. import __license__

        typer.echo(f"{__license__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version",
    ),
    license: bool = typer.Option(
        None,
        "--license",
        callback=license_callback,
        is_eager=True,
        help="Show license",
    ),
): ...


def find_pyproject_toml_config() -> Path | None:
    """Find the pyproject.toml file."""
    from black.files import find_pyproject_toml

    path = find_pyproject_toml((str(Path.cwd()),))
    if path is None:
        return None
    return Path(path)


def read_config(path: Path | None) -> dict[str, typing.Any]:
    """Read the configuration file."""

    # If no path is given, try to find the pyproject.toml file
    if path is None:
        path = find_pyproject_toml_config()

    # Return empty dict if no path is found
    if path is None:
        return {}

    # Try to read the configuration file
    try:
        # First try to use tomllib which is part of stdlib
        import tomllib as toml
    except ImportError:
        # If tomllib is not available, try to use toml
        try:
            import toml  # type: ignore
        except ImportError:
            typer.echo("Please install 'tomllib' or 'toml' to read configuration files")
            return {}

    try:
        config = toml.loads(Path(path).read_text())
    except Exception:
        typer.echo(f"Could not read configuration file {path}")
        return {}
    else:
        return config.get("tool", {}).get("gotranx", {})


@app.command()
def convert(
    fname: typing.Optional[Path] = typer.Argument(
        None,
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
    ),
    to: str = typer.Option(
        "",
        "--to",
        help="Generate code to another programming language",
    ),
    outname: typing.Optional[str] = typer.Option(
        None,
        "-o",
        "--outname",
        help="Output name",
    ),
    remove_unused: bool = typer.Option(
        False,
        "--remove-unused",
        help="Remove unused variables",
    ),
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version",
    ),
    license: bool = typer.Option(
        None,
        "--license",
        callback=license_callback,
        is_eager=True,
        help="Show license",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Verbose output",
    ),
    scheme: Annotated[
        typing.Optional[typing.List[Scheme]],
        typer.Option(help="Numerical scheme for solving the ODE"),
    ] = None,
    stiff_states: Annotated[
        typing.Optional[typing.List[str]],
        typer.Option(help="Stiff states for the hybrid rush larsen scheme"),
    ] = None,
    delta: float = typer.Option(
        1e-8,
        help="Delta value for the rush larsen schemes",
    ),
):
    warnings.warn(
        "convert command is deprecated, use ode2c, ode2py or cellml2ode instead",
        DeprecationWarning,
        stacklevel=1,
    )

    if fname is None:
        return typer.echo("No file specified")

    if to == "":
        # Check if outname is specified
        if outname is None:
            return typer.echo("No output name specified")
        else:
            to = Path(outname).suffix

    if to in {".c", ".h", "c"}:
        gotran2c.main(
            fname=fname,
            suffix=to,
            outname=outname,
            scheme=scheme,
            remove_unused=remove_unused,
            verbose=verbose,
            stiff_states=stiff_states,
            delta=delta,
        )
    if to in {".py", "python", "py"}:
        gotran2py.main(
            fname=fname,
            suffix=to,
            outname=outname,
            scheme=scheme,
            remove_unused=remove_unused,
            verbose=verbose,
            stiff_states=stiff_states,
            delta=delta,
        )

    if to in {".ode"}:
        from .cellml2ode import main as _main

        _main(fname=fname, outname=outname, verbose=verbose)


@app.command()
def cellml2ode(
    fname: typing.Optional[Path] = typer.Argument(
        None,
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
    ),
    outname: typing.Optional[str] = typer.Option(
        None,
        "-o",
        "--outname",
        help="Output name",
    ),
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version",
    ),
    license: bool = typer.Option(
        None,
        "--license",
        callback=license_callback,
        is_eager=True,
        help="Show license",
    ),
    config: typing.Optional[Path] = typer.Option(
        None,
        "--config",
        help="Read configuration options from a configuration file",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Verbose output",
    ),
):
    if fname is None:
        return typer.echo("No file specified")

    # config_data = read_config(config)
    from .cellml2ode import main as _main

    _main(fname=fname, outname=outname, verbose=verbose)


@app.command()
def ode2py(
    fname: typing.Optional[Path] = typer.Argument(
        None,
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
    ),
    to: str = typer.Option(
        "",
        "--to",
        help="Generate code to another programming language",
    ),
    outname: typing.Optional[str] = typer.Option(
        None,
        "-o",
        "--outname",
        help="Output name",
    ),
    remove_unused: bool = typer.Option(
        False,
        "--remove-unused",
        help="Remove unused variables",
    ),
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version",
    ),
    license: bool = typer.Option(
        None,
        "--license",
        callback=license_callback,
        is_eager=True,
        help="Show license",
    ),
    config: typing.Optional[Path] = typer.Option(
        None,
        "--config",
        help="Read configuration options from a configuration file",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Verbose output",
    ),
    scheme: Annotated[
        typing.Optional[typing.List[Scheme]],
        typer.Option(help="Numerical scheme for solving the ODE"),
    ] = None,
    stiff_states: Annotated[
        typing.Optional[typing.List[str]],
        typer.Option(help="Stiff states for the hybrid rush larsen scheme"),
    ] = None,
    delta: float = typer.Option(
        1e-8,
        help="Delta value for the rush larsen schemes",
    ),
    formatter: PythonFormatter = typer.Option(
        PythonFormatter.black,
        "--formatter",
        "-f",
        help="Formatter for the output code",
    ),
):
    if fname is None:
        return typer.echo("No file specified")

    # config_data = read_config(config)

    gotran2py.main(
        fname=fname,
        suffix=to,
        outname=outname,
        scheme=scheme,
        remove_unused=remove_unused,
        verbose=verbose,
        stiff_states=stiff_states,
        delta=delta,
    )


@app.command()
def ode2c(
    fname: typing.Optional[Path] = typer.Argument(
        None,
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
    ),
    to: str = typer.Option(
        "",
        "--to",
        help="Generate code to another programming language",
    ),
    outname: typing.Optional[str] = typer.Option(
        None,
        "-o",
        "--outname",
        help="Output name",
    ),
    remove_unused: bool = typer.Option(
        False,
        "--remove-unused",
        help="Remove unused variables",
    ),
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version",
    ),
    license: bool = typer.Option(
        None,
        "--license",
        callback=license_callback,
        is_eager=True,
        help="Show license",
    ),
    config: typing.Optional[Path] = typer.Option(
        None,
        "--config",
        help="Read configuration options from a configuration file",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Verbose output",
    ),
    scheme: Annotated[
        typing.Optional[typing.List[Scheme]],
        typer.Option(help="Numerical scheme for solving the ODE"),
    ] = None,
    stiff_states: Annotated[
        typing.Optional[typing.List[str]],
        typer.Option(help="Stiff states for the hybrid rush larsen scheme"),
    ] = None,
    delta: float = typer.Option(
        1e-8,
        help="Delta value for the rush larsen schemes",
    ),
    formatter: CFormatter = typer.Option(
        CFormatter.clang_format,
        "--formatter",
        "-f",
        help="Formatter for the output code",
    ),
):
    if fname is None:
        return typer.echo("No file specified")

    # config_data = read_config(config)

    gotran2c.main(
        fname=fname,
        suffix=to,
        outname=outname,
        scheme=scheme,
        remove_unused=remove_unused,
        verbose=verbose,
        stiff_states=stiff_states,
        delta=delta,
    )


@app.command()
def inspect(
    fname: typing.Optional[Path] = typer.Argument(
        None,
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
    ),
):
    typer.echo("Hello from inspect")
