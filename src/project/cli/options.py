import argparse
from typing import Any


class Option:
    """A reusable option object which delegates all arguments
    to parser.add_argument().
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs

    def add_to_parser(self, parser: argparse._ActionsContainer) -> None:
        parser.add_argument(*self.args, **self.kwargs)

    def add_to_group(self, group: argparse._ArgumentGroup) -> None:
        group.add_argument(*self.args, **self.kwargs)


class ArgumentGroup(Option):
    """A reusable argument group object which can call `add_argument()`
    to add more arguments. And itself will be registered to the parser later.
    """

    def __init__(
        self, name: str, is_mutually_exclusive: bool = False, required: bool = False
    ) -> None:
        self.name = name
        self.options: list[Option] = []
        self.required = required
        self.is_mutually_exclusive = is_mutually_exclusive

    def add_argument(self, *args: Any, **kwargs: Any) -> None:
        if args and isinstance(args[0], Option):
            self.options.append(args[0])
        else:
            self.options.append(Option(*args, **kwargs))

    def add_to_parser(self, parser: argparse._ActionsContainer) -> None:
        group: argparse._ArgumentGroup
        if self.is_mutually_exclusive:
            group = parser.add_mutually_exclusive_group(required=self.required)
        else:
            group = parser.add_argument_group(self.name)
        for option in self.options:
            option.add_to_group(group)

    def add_to_group(self, group: argparse._ArgumentGroup) -> None:
        self.add_to_parser(group)


verbose_option = ArgumentGroup("Verbosity options", is_mutually_exclusive=True)
verbose_option.add_argument(
    "-v",
    "--verbose",
    action="count",
    default=0,
    help="Use `-v` for detailed output and `-vv` for more detailed",
)
verbose_option.add_argument(
    "-q",
    "--quiet",
    action="store_const",
    const=-1,
    dest="verbose",
    help="Suppress output",
)
