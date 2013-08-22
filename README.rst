HG Commit Sanity
=======================

hg-commit-sanity is a Mercurial extension that allows to easily create precommit hooks to do sanity checks on commits.

Kudos to http://schinckel.net/2013/04/07/hg-commit---prevent-stupidity/

Installation
------------

::

    pip install hg-commit-sanity


Configuration
-------------

An example of your .hgrc::

  [extensions]
  hg-commit-sanity =

  [hg-commit-sanity]
  .py =
    ^[^#]*import pdb; pdb.set_trace\(\),
    ^print',
  .js =
    ^[^(//)]*console\.[a-zA-Z]+\(.*\)'

This will Abort the commit in case it will find import pdb; pdb.set_trace() in *.py files and console. in *.js files
