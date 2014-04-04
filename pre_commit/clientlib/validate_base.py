
from __future__ import print_function

import argparse
import jsonschema
import jsonschema.exceptions
import os.path
import yaml

from pre_commit.jsonschema_extensions import apply_defaults
from pre_commit.util import entry


def get_validator(
    json_schema,
    exception_type,
    additional_validation_strategy=lambda obj: None,
):
    """Returns a function which will validate a yaml file for correctness

    Args:
        json_schema - JSON schema to validate file with
        exception_type - Error type to raise on failure
        additional_validation_strategy - Strategy for additional validation of
            the object read from the file.  The function should either raise
            exception_type on failure.
    """
    def validate(filename, load_strategy=yaml.load):
        if not os.path.exists(filename):
            raise exception_type('File {0} does not exist'.format(filename))

        file_contents = open(filename, 'r').read()

        try:
            obj = load_strategy(file_contents)
        except Exception as e:
            raise exception_type(
                'File {0} is not a valid yaml file'.format(filename), e,
            )

        try:
            jsonschema.validate(obj, json_schema)
        except jsonschema.exceptions.ValidationError as e:
            raise exception_type(
                'File {0} is not a valid file'.format(filename), e,
            )

        obj = apply_defaults(obj, json_schema)

        additional_validation_strategy(obj)

        return obj

    return validate


def get_run_function(filenames_help, validate_strategy, exception_cls):
    @entry
    def run(argv):
        parser = argparse.ArgumentParser()
        parser.add_argument('filenames', nargs='*', help=filenames_help)
        args = parser.parse_args(argv)

        retval = 0
        for filename in args.filenames:
            try:
                validate_strategy(filename)
            except exception_cls as e:
                print(e.args[0])
                # If there was an inner exception, print the stringified
                # version of that.
                if len(e.args) > 1:
                    print(str(e.args[1]))
                retval = 1
        return retval
    return run