import sys, pathlib, re, shutil
rootpath = pathlib.Path(sys.argv[1]).resolve()
passed_args = sys.argv[2:]

cwd = []
line_num = 1

def resolve_path(path):
    result = []
    for name in path:
        if name == "." or name == "":
            continue
        elif name == "..":
            del result[-1]
        else:
            result.append(name)
    return result

def join_paths(*args):
    joined = []
    for path in args:
        for name in path:
            joined.append(name)
    return resolve_path(joined)

def get_full_path(*args):
    path = join_paths(*args)
    return rootpath.joinpath(*path)

def parse_path(path):
    split = path.split("/")
    if path[0] == "/":
        return resolve_path(split)
    else:
        return join_paths(cwd, split)

def write_file(content, path=None):
    if path == None:
        print(content, end="")
    else:
        parent = resolve_path(path)[:-1]
        get_full_path(parent).mkdir(parents=True, exist_ok=True)
        get_full_path(path).write_text(str(content))

def read_file(path=None, ignore_not_found=True):
    if path == None:
        return input()
    else:
        try:
            return get_full_path(path).read_text()
        except FileNotFoundError as e:
            if not ignore_not_found:
                error("File doesn't exist")
            return None

def delete_file(path):
    fullrmpath = get_full_path(path)
    if fullrmpath.exists():
        if fullrmpath.is_dir():
            shutil.rmtree(fullrmpath)
        else:
            fullrmpath.unlink()

def pluralize(count, word, plural=None):
    if plural == None:
        plural = word + "s"
    return f"{count} {plural if count != 1 else word}"

def error(err):
    print(f"\nError in {get_full_path(cwd, ['code.dir'])} line {line_num}:\n{err}")
    sys.exit(1)

filename_re = re.compile("^[/a-zA-Z0-9._-]+$")
def check_filename(name):
    if not filename_re.match(name):
        error(f"Invalid filename {name}, files can only have alphanumeric characters and . _ -")

def check_number(num):
    try:
        return float(num)
    except ValueError:
        error(f"Expected number, got {num}")
def get_int(num):
    check_number(num)
    try:
        return int(num)
    except ValueError:
        return int(float(num))

def cmd_cat(*args):
    return "".join(args)
exit_file = False
def cmd_cd(path):
    global exit_file, cwd
    newpath = parse_path(path)
    if get_full_path(newpath, ["code.dir"]).exists():
        cwd = newpath
        exit_file = True
def cmd_rm(path):
    delete_file(parse_path(path))
def cmd_read():
    return read_file()
def cmd_len(string):
    if string == None:
        return -1
    return len(string)
def cmd_head(size, string):
    if size == None or string == None:
        return ""
    size = get_int(size)
    if size <= 0:
        return ""
    return string[:size]
def cmd_tail(size, string):
    if size == None or string == None:
        return ""
    size = get_int(size)
    if size <= 0:
        return ""
    return string[-size:]
def cmd_add(*args):
    res = sum([check_number(n) for n in args])
    if int(res) == res:
        return int(res)
    return res
def cmd_sub(n1, n2):
    check_number(n1)
    check_number(n2)
    res = float(n1) - float(n2)
    if int(res) == res:
        return int(res)
    return res
def cmd_mul(*args):
    res = 1
    for n in args:
        res *= check_number(n)
    if int(res) == res:
        return int(res)
    return res
def cmd_div(n1, n2):
    check_number(n1)
    check_number(n2)
    if float(n2) == 0:
        error("Attempt to divide by 0")
    res = float(n1) / float(n2)
    if int(res) == res:
        return int(res)
    return res
def cmd_eq(arg1, arg2):
    try:
        if arg1 == arg2 or float(arg1) == float(arg2):
            return 1
    except:
        pass
    return 0
def cmd_lt(n1, n2):
    check_number(n1)
    check_number(n2)
    if float(n1) < float(n2):
        return 1
    return 0
def cmd_gt(n1, n2):
    check_number(n1)
    check_number(n2)
    if float(n1) > float(n2):
        return 1
    return 0
def cmd_ord(c):
    if len(c) != 1:
        error(f"Ord expects 1 character, got {len(c)}")
    return ord(c)
def cmd_chr(n):
    return chr(get_int(n))

commands = {
    "cat":  {"arg_count": "any", "output": True,  "missing_file": "",   "function": cmd_cat},
    "cd":   {"arg_count": 1,     "output": False, "missing_file": ".",  "function": cmd_cd},
    "rm":   {"arg_count": 1,     "output": False, "missing_file": ".",  "function": cmd_rm},

    "read": {"arg_count": 0,     "output": True,  "missing_file": "",   "function": cmd_read},

    "len":  {"arg_count": 1,     "output": True,  "missing_file": None, "function": cmd_len},
    "head": {"arg_count": 2,     "output": True,  "missing_file": None, "function": cmd_head},
    "tail": {"arg_count": 2,     "output": True,  "missing_file": None, "function": cmd_tail},

    "add":  {"arg_count": "any", "output": True,  "missing_file": 0,    "function": cmd_add},
    "sub":  {"arg_count": 2,     "output": True,  "missing_file": 0,    "function": cmd_sub},
    "mul":  {"arg_count": "any", "output": True,  "missing_file": 1,    "function": cmd_mul},
    "div":  {"arg_count": 2,     "output": True,  "missing_file": 1,    "function": cmd_div},

    "eq":   {"arg_count": 2,     "output": True,  "missing_file": None, "function": cmd_eq},
    "lt":   {"arg_count": 2,     "output": True,  "missing_file": 0,    "function": cmd_lt},
    "gt":   {"arg_count": 2,     "output": True,  "missing_file": 0,    "function": cmd_gt},

    "ord":  {"arg_count": 1,     "output": True,  "missing_file": "\0", "function": cmd_ord},
    "chr":  {"arg_count": 1,     "output": True,  "missing_file": 0,    "function": cmd_chr},
}

def run_line(tokens):
    global line_num
    cmd = None
    files = []
    has_output = False
    output_token = ""
    output = None
    output_append = False
    for token in tokens:
        if cmd == None:
            cmd = token
        elif has_output and (token == ">" or token == ">>"):
            error(f"Unexpected {token} after {output_token}")
        elif token == ">":
            has_output = True
            output_token = ">"
        elif token == ">>":
            has_output = True
            output_append = True
            output_token = ">>"
        elif has_output and output != None:
            error(f"Multiple file names after {output_token}")
        elif has_output:
            check_filename(token)
            output = token
        else:
            if token[0] != "$":
                check_filename(token)
            files.append(token)
    if has_output and output == None:
        error(f"Expected output file after {output_token}")
    try:
        cmd_info = commands[cmd]
    except KeyError:
        error(f"Unknown command: {cmd}")
    if cmd_info["arg_count"] != "any" and len(files) != cmd_info["arg_count"]:
        error(f"Command {cmd} expects {pluralize(cmd_info['arg_count'], 'file')}, {len(files)} passed")
    if not cmd_info["output"] and has_output:
        error(f"Attempt to store output of command {cmd} which doesn't output anything")
    cmd_args = []
    for name in files:
        content = None
        if name == "$#":
            cmd_args.append(str(len(passed_args)))
        elif name[0] == "$":
            try:
                num = int(name[1:])
                with open(passed_args[num], "r") as f:
                    content = f.read()
            except ValueError:
                error(f"Invalid argument name: {name}")
            except IndexError:
                content = None
        else:
            path = parse_path(name)
            content = read_file(path)
        if content == None:
            content = cmd_info["missing_file"]
        cmd_args.append(content)
    result = cmd_info["function"](*cmd_args)
    if cmd_info["output"]:
        if not has_output:
            write_file(result)
        else:
            path = parse_path(output)
            if output_append:
                result = read_file(path) + result
            write_file(result, path)
    line_num += 1

def run_code(path):
    global exit_file, line_num
    tokens = []
    cur_token = ""
    in_comment = False
    line_num = 1
    for char in read_file(path, False):
        if char == "\n":
            in_comment = False
            if cur_token != "":
                tokens.append(cur_token)
            cur_token = ""
            if len(tokens) > 0:
                run_line(tokens)
                if exit_file:
                    exit_file = False
                    return
            tokens = []
        elif in_comment:
            continue
        elif char == "#" and cur_token != "$":
            in_comment = True
        elif char == " ":
            if cur_token != "":
                tokens.append(cur_token)
            cur_token = ""
        else:
            cur_token += char
    if cur_token != "":
        tokens.append(cur_token)
    if len(tokens) > 0:
        run_line(tokens)
        if exit_file:
            exit_file = False
            return
    sys.exit(0)

while True:
    run_code(join_paths(cwd, ["code.dir"]))
