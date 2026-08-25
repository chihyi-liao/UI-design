import argparse
from argparse import _SubParsersAction
from collections.abc import Sequence
from typing import Any, Self

from ..options import Option, verbose_option


class BaseCommand:
    """A CLI subcommand"""

    # The subcommand's name
    name: str | None = None
    # The subcommand's help string, if not given, __doc__ will be used.
    description: str | None = None
    # A list of pre-defined options which will be loaded on initializing
    # Rewrite this if you don't want the default ones
    arguments: Sequence[Option] = (verbose_option,)

    @classmethod
    def init_parser(cls: type[Self], parser: argparse.ArgumentParser) -> Self:
        cmd = cls()
        for arg in cmd.arguments:
            arg.add_to_parser(parser)
        cmd.add_arguments(parser)
        return cmd

    @classmethod
    def register_to(
        cls, subparsers: _SubParsersAction, name: str | None = None, **kwargs: Any
    ) -> None:
        """Register a subcommand to the subparsers,
        with an optional name of the subcommand.
        """
        help_text = cls.description or cls.__doc__
        name = name or cls.name or ""
        # Remove the existing subparser as it will raise an error on Python 3.11+
        subparsers._name_parser_map.pop(name, None)
        subactions = subparsers._get_subactions()
        subactions[:] = [action for action in subactions if action.dest != name]
        parser = subparsers.add_parser(
            name,
            description=help_text,
            help=help_text,
            **kwargs,
        )
        command = cls.init_parser(parser)
        command.name = name
        parser.set_defaults(command=command)

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Manipulate the argument parser to add more arguments"""

    def handle(self, options: argparse.Namespace) -> None:
        """The command handler function.

        :param options: the parsed Namespace object
        """
        raise NotImplementedError
