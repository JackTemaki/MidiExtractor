import sys
import os
import pickle
from src.database import Database
from src.conditions import Condition


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".

    Taken from http://code.activestate.com/recipes/577058/
    MIT Licence
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def main():

    assert len(sys.argv) >= 2, "Missing command"

    command = sys.argv[1]

    if command == "create":
        assert len(sys.argv) == 4, "Invalid number of arguments for calling create"
        assert os.path.isdir(sys.argv[2]), "Provided path is not a folder"

        db = Database(sys.argv[2])
        db.export(sys.argv[3])

    if command == "extract":
        assert len(sys.argv) >= 3, "Invalid number of arguments for calling extract"
        assert os.path.isfile(sys.argv[1]), "Invalid database file"
        if os.path.isdir(sys.argv[2]):
            result = query_yes_no("Output path already exists, do you want to use it?", default='no')
            if not result:
                sys.exit(0)

        database_path = sys.argv[2]
        export_path = sys.argv[3]
        conditions = sys.argv[3:]

        db = pickle.load(open(database_path, "rb"))
        assert isinstance(db, Database), "File is not a valid database"

        condition = Condition(conditions)
        db.export_files(condition=condition, output_path=export_path)


if __name__ == '__main__':
    main()