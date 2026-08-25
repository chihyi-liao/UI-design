import argparse
import re
import sys
from argparse import Action, _ArgumentGroup
from collections.abc import Iterable
from typing import Any


class MyFormatter(argparse.RawDescriptionHelpFormatter):
    def start_section(self, heading: str | None) -> None:
        return super().start_section(heading.title() if heading else "")

    def _format_usage(
        self,
        usage: str | None,
        actions: Iterable[Action],
        groups: Iterable[_ArgumentGroup],
        prefix: str | None,
    ) -> str:
        if prefix is None:
            prefix = "Usage: "
        result = super()._format_usage(usage, actions, groups, prefix)  # type: ignore[arg-type]
        # Remove continuous spaces
        result = re.sub(r" +", " ", result)
        if prefix:
            return result.replace(prefix, prefix)
        return result

    def _format_action(self, action: Action) -> str:
        # determine the required width and the entry label
        help_position = min(self._action_max_length + 2, self._max_help_position)
        help_width = max(self._width - help_position, 11)
        action_width = help_position - self._current_indent - 2
        action_header = self._format_action_invocation(action)

        # no help; start on same line and add a final newline
        if not action.help:
            tup = "", self._current_indent, action_header
            action_header = "{0:>{1}}{2}\n".format(*tup)
            indent_first = None

        # short action name; start on the same line and pad two spaces
        elif len(action_header) <= action_width:
            tup = "", self._current_indent, action_header, action_width  # type: ignore[assignment]
            action_header = "{0:>{1}}{2:<{3}}  ".format(*tup)
            indent_first = 0

        # long action name; start on the next line
        else:
            tup = "", self._current_indent, action_header
            action_header = "{0:>{1}}{2}\n".format(*tup)
            indent_first = help_position

        # Special format for empty action_header
        # - No extra indent block
        # - Help info in the same indent level as subactions
        if not action_header.strip():
            action_header = ""
            help_position = self._current_indent
            indent_first = self._current_indent

        # collect the pieces of the action help
        parts = [action_header]

        # if there was help for the action, add lines of help text
        if action.help:
            help_text = self._expand_help(action)
            help_lines = []
            for help_line in help_text.split("\n"):
                help_lines += self._split_lines(help_line, help_width)
            parts.append("{:>{}}{}\n".format("", indent_first, help_lines[0]))
            for line in help_lines[1:]:
                parts.append("{:>{}}{}\n".format("", help_position, line))

        # or add a newline if the description doesn't end with one
        elif not action_header.endswith("\n"):
            if action_header:
                parts.append("\n")

        # cancel out extra indent when action_header is empty
        if not action_header:
            self._dedent()
        # if there are any sub-actions, add their help as well
        for subaction in self._iter_indented_subactions(action):
            parts.append(self._format_action(subaction))
        # cancel out extra dedent when action_header is empty
        if not action_header:
            self._indent()

        # return a single string
        return self._join_parts(parts)


class ArgumentParser(argparse.ArgumentParser):
    """A standard argument parser but with title-cased help."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if sys.version_info >= (3, 14):
            kwargs["color"] = False
        kwargs["formatter_class"] = MyFormatter
        kwargs["add_help"] = False
        super().__init__(*args, **kwargs)
        self.add_argument(
            "-h",
            "--help",
            action="help",
            default=argparse.SUPPRESS,
            help="Show this help message and exit.",
        )
        self._optionals.title = "options"
