r"""
   ________    ____
  / ____/ /   /  _/
 / /   / /    / /
/ /___/ /____/ /
\____/_____/___/
"""

import importlib
import pkgutil
import sys
from typing import cast

from . import commands
from .argparse import ArgumentParser
from .commands.base import BaseCommand

COMMANDS_MODULE_PATH = importlib.import_module(f"{commands.__name__}").__path__


def entrypoint():
    # 建立主解析器
    parser = ArgumentParser(prog="cli", description=__doc__)
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="version 1.0.0",
        help="Show the version and exit",
    )
    # 建立第一層子命令
    subparsers = parser.add_subparsers(
        parser_class=ArgumentParser, title="commands", metavar=""
    )
    for _finder, name, _ispkg in pkgutil.iter_modules(COMMANDS_MODULE_PATH):
        module = importlib.import_module(f"{commands.__name__}.{name}")
        try:
            cmd_cls = module.Command
        except AttributeError:
            continue

        # 註冊子命令
        cmd_cls.register_to(subparsers, cmd_cls.name or name)

    # 解析參數
    options = parser.parse_args()

    # 當註冊子命令後, 會將子命令 parser 綁定到 options.command
    command = cast("BaseCommand | None", getattr(options, "command", None))
    # 使用者沒輸入子命令
    if command is None:
        parser.print_help()
        sys.exit(0)

    # 執行子命令
    command.handle(options)
