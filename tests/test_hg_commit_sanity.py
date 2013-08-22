"""Tests for poke_jenkins hook."""
import contextlib
import os
import tempfile
import pytest

from mercurial import ui, hg, commands, util

import hg_commit_sanity


@pytest.fixture
def hg_ui():
    """Create test mercurial ui."""
    return ui.ui()


@pytest.fixture
def checkers():
    """Get checkers."""
    return {
        '.py': [
            '^[^#]*import pdb; pdb.set_trace\(\)',
            '^print'],
        '.js': ['^[^(//)]*console\.[a-zA-Z]+\(.*\)']
    }


@pytest.fixture
def hg_ui_with_checkers(hg_ui, checkers):
    """Get test mercurial ui with checkers config set up."""
    for key, value in checkers.items():
        hg_ui.setconfig('hg_commit_sanity', key, value)
    hg_commit_sanity.reposetup(hg_ui, hg_repo)
    return hg_ui


@pytest.fixture
def repo_dir():
    """Get test repo dir."""
    return tempfile.mkdtemp()


@pytest.fixture
def py_file_path(repo_dir):
    """Get test file path."""
    return os.path.join(repo_dir, 'file1.py')


@pytest.fixture
def hg_repo(hg_ui, repo_dir):
    """Get test mercurial repo."""
    commands.init(hg_ui, repo_dir)
    return hg.repository(hg_ui, repo_dir)


def test_hg_commit_sanity(hg_ui, hg_repo):
    """Test poke_jenkins hook setup."""
    hg_commit_sanity.reposetup(hg_ui, hg_repo)
    assert hg_ui.config('hooks', 'pretxncommit.hg-commit-sanity') == hg_commit_sanity.hg_commit_sanity_hook


def test_hg_commit_sanity_hook(
        hg_ui_with_checkers, hg_repo,
        py_file_path):
    """Test poke_jenkins hook with jenkins base url and repo url and jenkins jobs being set up."""

    with contextlib.closing(open(py_file_path, 'a')) as f:
        f.write('import pdb; pdb.set_trace()')

    with pytest.raises(util.Abort) as exc:
        commands.commit(hg_ui_with_checkers, hg_repo, py_file_path, message="A test", addremove=True)

    assert 'Unable to commit. There were errors in 1 files.' in exc.value.args[0]
