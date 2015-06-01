import os
import sys
import errno
from cdm_generator import CDMGenerator
from code_generator import CodeGenerator

__author__ = 'jzaczek'

directory_commands = ["from-data", "from-config"]
usage_commands = ["usage", "help"]
valid_commands = directory_commands + usage_commands
valid_flags = "p"


def execute_command(command, file_location, flags):
    if command == "help" or command == "usage":
        usage()
    if command == "from-data":
        from_data(file_location, flags)
    if command == "from-config":
        from_config(file_location, flags)
        pass


def usage():
    print "\n\nCommands: " + str(valid_commands) + "\n"
    print "  help, usage"
    print "    prints this message\n"
    print "  from-data"
    print "    Requires passing [directory-name] as a next argument. Parses *.json files in the [directory-name],\n" \
          "    creates json Canonical Data Model in [directory-name]/config/ and prints out Swift classes code\n" \
          "    for provided json files\n"
    print "    usage: json2code.py from-data [directory-name] [flags]\n"
    print "  from-config"
    print "    Requires passing [directory-name] as a next argument. Parses *.json files in the [directory-name]\n" \
          "    as CDM data and prints out Swift classes code for provided json files\n"
    print "    usage: json2code.py from-config [directory-name]\n"
    print "Flags:" + flags + "\n"
    print "  -p"
    print "    Switches data reference prediction on. This means that fields which names contain 'id' or 'uri',\n" \
          "    or the values of which contain other json objects, will be treated as references to other classes\n\n"


def from_data(floc, fl):
    if not floc.endswith("/"):
        floc += "/"

    config_location = floc + "config"

    predict_references = False
    if "p" in fl:
        predict_references = True

    try:
        os.mkdir(config_location)
    except OSError as e:
        if e.errno != 17:
            print e
            sys.exit(-1)

    cdm_gen = CDMGenerator(floc, config_location, predict_references=predict_references)
    cdm_gen.generate()
    code_gen = CodeGenerator(config_location)
    code_gen.generate()


def from_config(floc, fl):
    predict_references = False
    if "p" in fl:
        predict_references = True

    code_gen = CodeGenerator(floc)
    code_gen.generate()


if __name__ == "__main__":
    flags = ""
    file_location = ""

    if len(sys.argv) < 2:
        print "Please specify command - type \"json2code.py help\" for valid command list"
        sys.exit(-1)

    command = sys.argv[1]

    if command in directory_commands:
        if len(sys.argv) < 3:
            print "Please specify directory"
            sys.exit(-1)
        else:
            file_location = sys.argv[2]

        if len(sys.argv) == 4:
            flags = sys.argv[3][1:]
            for flag in flags:
                if flag not in valid_flags:
                    print "Invalid flag value, type \"json2code.py help\" for usage examples"
                    sys.exit(-1)


    execute_command(command, file_location, flags)