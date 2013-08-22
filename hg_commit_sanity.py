"""A simple extension that fires a Jenkins job for incoming heads.

This file is part of poke_jenkins.

poke_jenkins is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

poke_jenkins is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with poke_jenkins.  If not, see <http://www.gnu.org/licenses/>.

"""
import os.path
import re

from mercurial import util


class colour(object):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'

ERROR_HEADER = "*** Unable to commit. There were errors in {0} files. ***"
ERROR_MESSAGE = """  File "{0}/{1}", line {2},
{3}{4}{5}"""


def test_data(checkers, data):
    for checker in checkers:
        for match in checker.finditer(data):
            line_number = data[:match.end()].count('\n')
            print 'yield', line_number
            yield line_number + 1, data.split('\n')[line_number]


def hg_commit_sanity_hook(ui, repo, node=None, **kwargs):
    checkers = {}
    for key, value in ui.configitems('hg_commit_sanity'):
        if key.startswith('.'):
            checkers[key] = [re.compile(item) for item in value.splitlines()]

    changeset = repo[node]

    errors = {}

    for filename in changeset:
        ext = os.path.splitext(filename)[-1]
        checkers = checkers.get(ext)
        if checkers:
            data = changeset.filectx(filename).data()
            our_errors = list(test_data(checkers, data))
            if our_errors:
                errors[filename] = our_errors

    lines = []

    if errors:
        lines.append(colour.HEADER + ERROR_HEADER.format(len(errors)) + colour.END)
        for filename, error_list in errors.items():
            for line_number, message in error_list:
                lines.append(ERROR_MESSAGE.format(
                    repo.root, filename, line_number,
                    colour.FAIL, message, colour.END,
                ))
        raise util.Abort('\n'.join(lines))


def reposetup(ui, repo):
    """Set up the the hook."""
    ui.setconfig("hooks", "pretxncommit.hg-commit-sanity", hg_commit_sanity_hook)
