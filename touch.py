#!/usr/bin/python3

from colorama import Fore, Style
from datetime import datetime
from filedate import File as FiledateFile
from os import listdir, path, stat, sys, utime
from os import name as osname
from time import time

from utility.argument_parsers import parser
from utility.cli import create_spinner, pl, print_while_spinning
from utility.windows import is_safe_regarding_windows_timestamp_bug 

TAB_LENGTH = 2

def get_decorative_print_descent_prefix(level, folder : bool = True):
    decoration_count = ((level * TAB_LENGTH)) + (0 if folder else TAB_LENGTH)
    return f"{'' if folder else '  '}{'-' * decoration_count}{'|' if folder else '-'}"

def get_system_time_as_datetime(system_time = None):
    if system_time is None:
        system_time = time()
    return datetime.fromtimestamp(system_time)

def get_file_time_as_datetime(absolute_file_path, path_get_time_function_name):
    path_get_time_function = getattr(path, path_get_time_function_name)
    return get_system_time_as_datetime(path_get_time_function(absolute_file_path))

def get_file_time_as_datetime_by_keyword(absolute_file_path, time_keyword):
    # Translate:
    # - created  -> c
    # - modified -> m
    # - accessed -> a
    keyword_part = time_keyword[0]
    path_get_time_function_name = f"get{keyword_part}time"
    return get_file_time_as_datetime(absolute_file_path, path_get_time_function_name)

def is_datetime_time_old(args, time):
    return (time - args.old).days <= 0

def print_file_info(args, level : int, file_name : str, performed_action : bool, success : bool = True, reason : str = None, spinner=None):
    if (not success) or (not args.silent):
        file_deco = get_decorative_print_descent_prefix(level, folder=False)
        if performed_action:
            if success:
                print_while_spinning(f"{file_deco} {file_name} updated.", spinner=spinner, dim=False, color=Fore.GREEN)
            else:
                print_while_spinning(f"{file_deco} {file_name} not updated ({reason or 'error occurred'}).", spinner=spinner, dim=False, color=Fore.RED, appendix=reason)    
        elif success:
            print_while_spinning(f"{file_deco} {file_name} not updated.{Fore.WHITE}{Style.DIM} ({reason})", spinner=spinner, dim=False, color=Fore.BLUE)

def descent_into_folder(args, absolute_folder_path=None, level=0):
    # absolute_folder_path is allowed to be None iff level is 0
    if (absolute_folder_path is None) != (level == 0):
        raise RuntimeError(f"Call to descent_into_folder() with {absolute_folder_path=}, {level=} not intended.")
    
    # Use the top level folder, if level is 0
    absolute_folder_path = absolute_folder_path or args.scan_path
    folder_name = path.basename(absolute_folder_path)
    decoration = get_decorative_print_descent_prefix(level)
    should_info_to_stdout = level == 0 or not args.silent
    spinner = None
    if should_info_to_stdout:
        spinner = create_spinner(f"{decoration} {folder_name}")

    ### Handle files in this folder first, then descent into children
    ## Handle files
    # TODO: Handle access permission errors
    # Stop spinner spin and change to info
    if should_info_to_stdout:
        spinner.info()
    child_paths = [p for p in listdir(absolute_folder_path)]
    level_folders = [p for p in child_paths if path.isdir(path.join(absolute_folder_path, p))]
    level_files = [p for p in child_paths if not path.isdir(path.join(absolute_folder_path, p))]
    found_files_count, touched_files_count = 0, 0
    for file_name in level_files:
        absolute_file_path = path.join(absolute_folder_path, file_name)
        if handle_file(args, file_name, absolute_file_path, level, is_file=True, spinner=spinner):
            touched_files_count += 1
        found_files_count += 1

    ## Descent into folders
    for child_folder_name in level_folders:
        absolute_child_folder_path = path.join(absolute_folder_path, child_folder_name)
        lower_level = level + 1
        child_found, child_touched = descent_into_folder(args, absolute_child_folder_path, lower_level)
        found_files_count += child_found
        touched_files_count += child_touched

    # Files of this folder is completed. Check for the folder itself now.
    level_above = max(level - 1, 0)
    if handle_file(args, folder_name, absolute_folder_path, level_above, is_file=False, spinner=spinner):
        touched_files_count += 1
    found_files_count += 1

    # This folder is completed, print information
    step_style = Style.DIM if level > 0 else Style.NORMAL
    step_color = Fore.WHITE if level > 0 else Fore.GREEN
    if should_info_to_stdout:
        spinner.succeed(f"{decoration} {folder_name} scanned.\t {step_style}{step_color} Checked: {found_files_count}\t Modified: {touched_files_count}{Style.RESET_ALL}")
    return found_files_count, touched_files_count

def handle_file(args, file_name, absolute_file_path, level, is_file=True, spinner=None):
    current_time_dict = {
        time_keyword: get_file_time_as_datetime_by_keyword(absolute_file_path, time_keyword)
        for time_keyword in ("created", "modified", "accessed")
    }
    is_time_old_dict = {
        time_keyword: is_datetime_time_old(args, current_time_dict[time_keyword])
        for time_keyword in current_time_dict
    }

    file_size = stat(absolute_file_path).st_size
    is_any_time_old = any(is_time_old_dict.values())
    if is_file:
        perform_action = is_any_time_old and (file_size > 0 or args.update_empty)
    else:
        perform_action = is_any_time_old and args.update_dirs

    if perform_action:
        current_system_time = get_system_time_as_datetime()

        patched_times = {
            time_keyword: current_system_time if is_time_old_dict[time_keyword] else current_time_dict[time_keyword]
            for time_keyword in current_time_dict
        }

        # Check for Python timestamp() bug on Windows
        # Reference: https://github.com/python/cpython/issues/94414
        if sys.platform.startswith("win") and \
                not is_safe_regarding_windows_timestamp_bug(patched_times.values()):
            print_file_info(args, level, file_name, perform_action, success=False, reason="skipped as the new file time is not supported by Windows", spinner=spinner)
            return False

        filedate_obj = FiledateFile(absolute_file_path)
        filedate_obj.set(**patched_times)
    
    if is_any_time_old:
        print_file_info(args, level, file_name, perform_action, success=True, reason="skipped as the file is empty", spinner=spinner)
        return True

def main(args):
    old_time_str = args.old.strftime('%Y-%m-%d')
    create_spinner().info(f"Scanning for old files (<= {old_time_str}) in: {args.scan_path}")
    descent_into_folder(args)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
