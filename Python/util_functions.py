import os
import re
from time import strftime, localtime

def get_dir_files(dir, file_types=[]):
    """
    Returns a list of all files in the given directory and its subdirectories if they have the extensions listed in file_types.
    
    Parameters:
    dir (str): The directory path to search for files.
    file_types (list): The file types its seaching for. leave blank for no filters
    
    Returns:
    list: A list of file paths.
    """
    create_dir(dir)
    files_list = []
    # Walk through the directory
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.split(".")[-1].lower() in file_types or file_types==[]:
                # Get the full path of the file and add to the list
                files_list.append(os.path.join(root, file))

    if files_list == []:
        raise FileNotFoundError("No files in directory. the dir has been created please populate it")
    return files_list

# Example usage:
# files = get_dir_files('/path/to/directory')
# print(files)

def create_dir(dir):
    """
    Creates the Directory if it does not already exist
    
    Parameters:
    dir (str): The directory path to create.
    
    """
    if not os.path.exists(dir):
        os.makedirs(dir)
        print(f"Directory '{dir}' created.")

def list_into_empty_dict(data_list):
    """
    Creates a dictionary with keys of the list inputed and empty values
    
    Parameters:
        data_list (list): list of wanted keys.
    Returns:
        (dict): Dictionary full of keys
    """
    output = {}
    for item in data_list:
        output[item] = ""
    return output


def convert_epoch(epoch_time, format='%Y-%m-%d %H:%M:%S'):
    return strftime(format, localtime(int(epoch_time) / 1000))

