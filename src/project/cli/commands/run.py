import argparse

from pandas.core.reshape.encoding import from_dummies

from ..options import verbose_option
from .base import BaseCommand


class Command(BaseCommand):
    """執行指令"""

    arguments = (verbose_option,)
    name = "run"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        subparser = parser.add_subparsers(title="commands", metavar="")
        Example01Command.register_to(subparser)
        Example02Command.register_to(subparser)

        self.parser = parser

    def handle(self, options: argparse.Namespace) -> None:
        self.parser.print_help()


class Example01Command(BaseCommand):
    name = "example01"

    def handle(self, options: argparse.Namespace) -> None:
        """執行位置"""
        from project.examples import ex01

        ex01.main()


class Example02Command(BaseCommand):
    name = "example02"

    def handle(self, options: argparse.Namespace) -> None:
        """執行位置"""
        from project.examples import ex02

        ex02.main()
