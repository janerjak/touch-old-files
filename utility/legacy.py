from tof.touch import get_file_time_as_datetime

def get_creation_time_as_datetime(absolute_file_path):
    return get_file_time_as_datetime(absolute_file_path, "getctime")

def get_modification_time_as_datetime(absolute_file_path):
    return get_file_time_as_datetime(absolute_file_path, "getmtime")

def get_access_time_as_datetime(absolute_file_path):
    return get_file_time_as_datetime(absolute_file_path, "getatime")