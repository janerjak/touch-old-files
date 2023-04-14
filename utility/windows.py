def is_safe_regarding_windows_timestamp_bug(file_times):
    try:
        for file_time in file_times:
            file_time.timestamp()
    except OSError:
        return False
    return True