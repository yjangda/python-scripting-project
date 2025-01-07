import os 
import json
import shutil
#allows us to run shell commands
from subprocess import PIPE, run 
import sys

GAME_DIR_PATTERN = 'game'
GAME_CODE_EXTENSION = '.go'
GAME_COMPILE_COMMAND = ['go', 'build']

def find_all_game_paths(source):
    game_paths = []
    #walk recjursively through the source directory
    #gives root directory, directories, and files in the current level
    for root, dirs, files in os.walk(source):
        for directories in dirs:
            if GAME_DIR_PATTERN in directories.lower():
                #need path later so def it seprarately
                path = os.path.join(source, directories)
                game_paths.append(path)

        break
    return game_paths

def get_name_from_paths(paths, to_strip):
    new_names = []
    for path in paths:
        #splits the path into the directory and the name
        _, dir_name = os.path.split(path)
        new_dir_name = dir_name.replace(to_strip, '')
        new_names.append(new_dir_name)
    return new_names

def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def copy_and_overwrite(source, dest):
    if os.path.exists(dest):
        #recursive delete
        shutil.rmtree(dest)
    shutil.copytree(source, dest)

def make_json_metadata_file(path, game_dirs):
    data = {
        "gameNames": game_dirs,
        "number_of_games": len(game_dirs)
    }

    #context manager: with closes file for us
    with open(path, 'w') as f:
        #dump[s] dumps it as string dump dumps it as json
        json.dump(data, f)

#path to the directory where game code is compiled
def compile_game_code(path):
    code_file_name = None
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(GAME_CODE_EXTENSION):
                code_file_name = file
                break

        break

    if code_file_name is None:
        return
    
    command = GAME_COMPILE_COMMAND + [code_file_name]
    run_command(command, path)

def run_command(command, path):
    cwd = os.getcwd()
    os.chdir(path)

    #PIPE allows us to
    result = run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True)
    print("compile result", result)

    os.chdir(cwd)

def main(source, target):
    #working directory
    cwd = os.getcwd()
    #joins correct path based on OS, concatenates the current working directory with the source directory
    source_path = os.path.join(cwd, source)
    target_path = os.path.join(cwd, target)
    #original game paths
    game_paths = find_all_game_paths(source_path)
    #new game paths with _game removed
    new_game_dirs = get_name_from_paths(game_paths, "_game")

    create_dir(target_path)

    #zip takes mathcing elements from two lists and combines them into a tuple
    for src, dest in zip(game_paths, new_game_dirs):
        dest_path = os.path.join(target_path, dest)
        copy_and_overwrite(src, dest_path)
        compile_game_code(dest_path)

    json_path = os.path.join(target_path, 'metadata.json')
    make_json_metadata_file(json_path, new_game_dirs)

if __name__ == '__main__':
    args = sys.argv
    if len(args) !=3:
        raise Exception("Source and destination directories only")
    
    source, target = args[1:]
    main(source, target)