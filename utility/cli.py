from colorama import Fore, Style
from halo import Halo
from inflect import engine as plural_engine_generator

plural_engine = plural_engine_generator()

def pl(noun : str, quantity : int):
    return plural_engine.plural_noun(noun, quantity)

def print_while_spinning(msg : str, appendix : str = None, exit_code : int = None, spinner : Halo = None, dim : bool = True, color : str = Fore.RED):
    if spinner is not None:
        spinner.stop()
    print(f"{Style.DIM if dim else ''}{color}{msg}", end="")
    if appendix:
        print(f"\n{Fore.WHITE}{appendix}", end="")
    print(Style.RESET_ALL)
    if exit_code is not None:
        exit(exit_code)
    if spinner is not None:
        spinner.start()

def print_error(error_msg : str, error_appendix : str = None, exit_code : int = None, spinner : Halo = None):
    print_while_spinning(error_msg, error_appendix, exit_code, spinner, dim=True, color=Fore.RED)

def create_spinner(msg : str = None, start : bool = True):
    spinner = Halo(text=msg if msg is not None else "Working on it", spinner="dots")
    if start:
        spinner.start()
    return spinner

def create_done_spinner(msg : str, spinner_method, cond : bool = True):
    if cond:
        spinner = create_spinner(msg, False)
        (getattr(spinner, spinner_method))()

def fail_spinner_exit(spinner, persistent_msg : str = None, exit_code : int = 1, exception : BaseException = None):
    if persistent_msg:
        spinner.fail(persistent_msg)
    else:
        spinner.fail()
    if exception is not None:
        print(f"{Style.NORMAL}{Fore.WHITE}Exception info:\n{Style.DIM}{exception}{Style.RESET_ALL}")
    exit(exit_code)