import sys
import os
import subprocess
import difflib
import re


commands_builtin = []
current_path = ""

def check_command_from_path(cmd):
    PATH_var = os.environ["PATH"]
    PATH_ls = PATH_var.split(":")
    
    for path in PATH_ls:
        if os.path.exists(f"{path}/{cmd}"):
            return True, path
    return False, None

def fun_ls(path):
    return '\n'.join(os.listdir(path))

def fun_echo(cmd):
    if cmd.startswith("'"):
        return cmd[1:-1]
    elif cmd.startswith('"'):
        return re.sub(r'\\(.)', r'\1', cmd[1:-1])
    else:
        return " ".join(cmd.split())

def fun_cat(files):
    output = []
    for file in files:
        if os.path.exists(file):
            with open(file, "r") as f:
                output.append(f.read())
        else:
            return f"cat: {file}: No such file or directory"
    return "\n".join(output)

def fun_mkdir(path):
    try:
        os.makedirs(path, exist_ok=True)
        return ""
    except Exception as e:
        return str(e)

def fun_rmdir(path):
    try:
        os.rmdir(path)
        return ""
    except Exception as e:
        return str(e)

def fun_rm(path):
    try:
        os.remove(path)
        return ""
    except Exception as e:
        return str(e)

def fun_touch(path):
    try:
        with open(path, 'a'):
            os.utime(path, None)
        return ""
    except Exception as e:
        return str(e)

def output_redirection(cmd, op_file):
    cmd_name, args = cmd.split(maxsplit=1)
    output = ""

    if cmd_name == "echo":
        output = fun_echo(args)
    elif cmd_name == "cat":
        output = fun_cat(args.split())
    elif cmd_name == "ls":
        output = fun_ls(args)

    with open(op_file, "w") as f:
        f.write(output)

def execute_command(cmd):
    global current_path

    if cmd == "exit 0":
        exit(0)

    if cmd.startswith("echo"):
        print(fun_echo(cmd[5:]))

    elif cmd.startswith("cat"):
        print(fun_cat(cmd[4:].split()))

    elif cmd.startswith("ls"):
        path = cmd[3:].strip() or current_path
        print(fun_ls(path))

    elif cmd.startswith("pwd"):
        print(current_path)

    elif cmd.startswith("cd"):
        change_path = cmd[3:].strip()
        if change_path == "~":
            current_path = os.environ["HOME"]
        elif os.path.isabs(change_path) and os.path.exists(change_path):
            current_path = change_path
        elif os.path.exists(os.path.join(current_path, change_path)):
            current_path = os.path.realpath(os.path.join(current_path, change_path))
        else:
            print(f"cd: {change_path}: No such file or directory")

    elif cmd.startswith("mkdir"):
        path = cmd[6:].strip()
        print(fun_mkdir(path))

    elif cmd.startswith("rmdir"):
        path = cmd[6:].strip()
        print(fun_rmdir(path))

    elif cmd.startswith("rm"):
        path = cmd[3:].strip()
        print(fun_rm(path))

    elif cmd.startswith("touch"):
        path = cmd[6:].strip()
        print(fun_touch(path))

    elif cmd == "clear":
        os.system("clear")

    elif cmd.find(">") != -1:
        parts = cmd.split(">", maxsplit=1)
        execute_command(parts[0].strip())
        output_redirection(parts[0].strip(), parts[1].strip())

    else:
        try:
            subprocess.run(cmd.split(), check=True)
        except FileNotFoundError:
            print(f"{cmd}: command not found")

def main():
    global current_path
    global commands_builtin

    commands_builtin = ["echo", "cat", "ls", "pwd", "cd", "mkdir", "rmdir", "rm", "touch", "exit", "clear", "type"]
    current_path = os.getcwd()

    while True:
        cmd = input(f"{current_path}$ ").strip()
        if cmd:
            if cmd.split()[0] not in commands_builtin:
                suggestions = difflib.get_close_matches(cmd, commands_builtin)
                if suggestions:
                    print(f"Did you mean: {', '.join(suggestions)}?")
                else:
                    print(f"Command '{cmd}' not recognized.")
            else:
                execute_command(cmd)
        print()

if __name__ == "__main__":
    main()
