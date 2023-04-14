from argparse import ArgumentParser, ArgumentTypeError, ArgumentDefaultsHelpFormatter
from datetime import datetime
from os import path


def folder_argument(value):
    if not isinstance(value, str):
        raise ArgumentTypeError(f"'{value}' to be converted to path is not a string")
    if not path.isdir(value):
        raise ArgumentTypeError(f"'{value}' is not a valid path or not accessible")
    return path.abspath(value)

def date_argument(value: str):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except Exception as ex:
        raise ArgumentTypeError(f"'{value}' is not a valid date with format YYYY-mm-dd.\nFurther information:\n{ex}")

def positive_int_or_none(value):
    ivalue = None
    if ivalue is not None:
        ivalue = int(value)
        if ivalue <= 0:
            raise ArgumentTypeError(f"{value} is not a positive integer or None")
    return ivalue

parser = ArgumentParser(
    description="Touches files that are older those modification dates are at least as old as specified",
    formatter_class=ArgumentDefaultsHelpFormatter,
)

task_group = parser.add_argument_group("task", description="Arguments to specify the tasks to be completed")
task_group.add_argument("--scan-path", "-i", type=folder_argument, default="./", help="path to the folder which is scanned recursively")
task_group.add_argument("--old", "-o", type=date_argument, default="1970-01-01", help="files with modification times equal to or older than this argument are touched. Default is date of UNIX time 0. Format: YYYY-mm-dd")
task_group.add_argument("--update-empty", "-0", action="store_true", help="update times of empty files. Turned off by default.")
task_group.add_argument("--update-dirs", "-d", type=bool, default=True, help="whether to update times of directories")

io_group = parser.add_argument_group("io", description="Arguments to specify inputs and outputs")
io_group.add_argument("--silent", "-s", action="store_true", help="disable verbose STDOUT output and print success and error information")

misc_group = parser.add_argument_group("misc", "Miscellaneous arguments")
misc_group.add_argument("--depth-limit", "-L", type=positive_int_or_none, default=None, help="depth limit for recursive folder scanning. Set this to a positive value if for instance symlinks point to upper level directories")