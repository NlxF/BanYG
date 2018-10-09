from datetime import datetime
try:
    from flask_script import Manager
except ImportError:
    raise Exception("flask_script not found!")
try:
    from flask_migrate import (init, revision, migrate, edit, merge, upgrade, downgrade,
                               show, history, heads, branches, current, stamp)
except ImportError:
    raise Exception("flask_migrate not found!")
from bwg360.models.download import DownloadRecord, DBTag


MyMigrateCommand = Manager(usage='custom db migrations for table sharding')


@MyMigrateCommand.option('-d', '--directory', dest='directory', default=None,
                   help=("migration script directory (default is "
                         "'migrations')"))
@MyMigrateCommand.option('--multidb', dest='multidb', action='store_true',
                   default=False, help=("Multiple databases migraton (default is "
                         "False)"))
def minit(directory=None, multidb=False):

    init(directory=None, multidb=False)


@MyMigrateCommand.option('--rev-id', dest='rev_id', default=None,
                         help=('Specify a hardcoded revision id instead of '
                               'generating one'))
@MyMigrateCommand.option('--version-path', dest='version_path', default=None,
                         help=('Specify specific path from config for version '
                               'file'))
@MyMigrateCommand.option('--branch-label', dest='branch_label', default=None,
                         help=('Specify a branch label to apply to the new '
                               'revision'))
@MyMigrateCommand.option('--splice', dest='splice', action='store_true',
                         default=False,
                         help=('Allow a non-head revision as the "head" to '
                               'splice onto'))
@MyMigrateCommand.option('--head', dest='head', default='head',
                         help=('Specify head revision or <branchname>@head to '
                               'base new revision on'))
@MyMigrateCommand.option('--sql', dest='sql', action='store_true', default=False,
                         help=("Don't emit SQL to database - dump to standard "
                               "output instead"))
@MyMigrateCommand.option('--autogenerate', dest='autogenerate',
                         action='store_true', default=False,
                         help=('Populate revision script with candidate '
                               'migration operations, based on comparison of '
                               'database to model'))
@MyMigrateCommand.option('-m', '--message', dest='message', default=None,
                         help='Revision message')
@MyMigrateCommand.option('-d', '--directory', dest='directory', default=None,
                         help=("migration script directory (default is "
                               "'migrations')"))
def mrevision(directory=None, message=None, autogenerate=False, sql=False,
             head='head', splice=False, branch_label=None, version_path=None,
             rev_id=None):
    revision(directory=None, message=None, autogenerate=False, sql=False,
             head='head', splice=False, branch_label=None, version_path=None,
             rev_id=None)


@MyMigrateCommand.option('--rev-id', dest='rev_id', default=None,
                         help=('Specify a hardcoded revision id instead of '
                               'generating one'))
@MyMigrateCommand.option('--version-path', dest='version_path', default=None,
                         help=('Specify specific path from config for version '
                               'file'))
@MyMigrateCommand.option('--branch-label', dest='branch_label', default=None,
                         help=('Specify a branch label to apply to the new '
                               'revision'))
@MyMigrateCommand.option('--splice', dest='splice', action='store_true',
                         default=False,
                         help=('Allow a non-head revision as the "head" to '
                               'splice onto'))
@MyMigrateCommand.option('--head', dest='head', default='head',
                         help=('Specify head revision or <branchname>@head to '
                               'base new revision on'))
@MyMigrateCommand.option('--sql', dest='sql', action='store_true', default=False,
                         help=("Don't emit SQL to database - dump to standard "
                               "output instead"))
@MyMigrateCommand.option('-m', '--message', dest='message', default=None)
@MyMigrateCommand.option('-d', '--directory', dest='directory', default=None,
                         help=("migration script directory (default is "
                               "'migrations')"))
@MyMigrateCommand.option('-x', '--x-arg', dest='x_arg', default=None,
                         action='append', help=("Additional arguments consumed "
                                                "by custom env.py scripts"))
def mmigrate(directory=None, message=None, sql=False, head='head', splice=False,
            branch_label=None, version_path=None, rev_id=None, x_arg=None):

    _tag = DBTag.query.limit(1).first()
    start_tag = _tag.tag
    if start_tag:
        old_table = DownloadRecord.model(start_tag)

        start_year  = int(start_tag[:-2])
        start_month = int(start_tag[-2:])
        now_year  = datetime.utcnow().year
        now_month = datetime.utcnow().month

        interval_month = (now_year-start_year) * 12 + (now_month-start_month)
        for idx in range(interval_month):
            total_month = start_month + idx
            record_tag = '{:4d}{:02d}'.format(start_year + total_month // 12, total_month % 12 + 1)
            old_table = DownloadRecord.model(record_tag)

    latest_table = DownloadRecord.model()

    migrate(directory=None, message=None, sql=False, head='head', splice=False,
            branch_label=None, version_path=None, rev_id=None, x_arg=None)


@MyMigrateCommand.option('revision', nargs='?', default='head',
                         help="revision identifier")
@MyMigrateCommand.option('-d', '--directory', dest='directory', default=None,
                         help=("migration script directory (default is "
                               "'migrations')"))
def medit(directory=None, revision='current'):

    edit(directory=None, revision='current')


@MyMigrateCommand.option('--rev-id', dest='rev_id', default=None,
                         help=('Specify a hardcoded revision id instead of '
                               'generating one'))
@MyMigrateCommand.option('--branch-label', dest='branch_label', default=None,
                         help=('Specify a branch label to apply to the new '
                               'revision'))
@MyMigrateCommand.option('-m', '--message', dest='message', default=None)
@MyMigrateCommand.option('revisions', nargs='+',
                         help='one or more revisions, or "heads" for all heads')
@MyMigrateCommand.option('-d', '--directory', dest='directory', default=None,
                         help=("migration script directory (default is "
                               "'migrations')"))
def mmerge(directory=None, revisions='', message=None, branch_label=None,
          rev_id=None):

    merge(directory=None, revisions='', message=None, branch_label=None,
          rev_id=None)


@MyMigrateCommand.option('--tag', dest='tag', default=None,
                         help=("Arbitrary 'tag' name - can be used by custom "
                               "env.py scripts"))
@MyMigrateCommand.option('--sql', dest='sql', action='store_true', default=False,
                         help=("Don't emit SQL to database - dump to standard "
                               "output instead"))
@MyMigrateCommand.option('revision', nargs='?', default='head',
                         help="revision identifier")
@MyMigrateCommand.option('-d', '--directory', dest='directory', default=None,
                         help=("migration script directory (default is "
                               "'migrations')"))
@MyMigrateCommand.option('-x', '--x-arg', dest='x_arg', default=None,
                         action='append', help=("Additional arguments consumed "
                                                "by custom env.py scripts"))
def mupgrade(directory=None, revision='head', sql=False, tag=None, x_arg=None):

    upgrade(directory=None, revision='head', sql=False, tag=None, x_arg=None)


@MyMigrateCommand.option('--tag', dest='tag', default=None,
                         help=("Arbitrary 'tag' name - can be used by custom "
                               "env.py scripts"))
@MyMigrateCommand.option('--sql', dest='sql', action='store_true', default=False,
                         help=("Don't emit SQL to database - dump to standard "
                               "output instead"))
@MyMigrateCommand.option('revision', nargs='?', default="-1",
                         help="revision identifier")
@MyMigrateCommand.option('-d', '--directory', dest='directory', default=None,
                         help=("migration script directory (default is "
                               "'migrations')"))
@MyMigrateCommand.option('-x', '--x-arg', dest='x_arg', default=None,
                         action='append', help=("Additional arguments consumed "
                                                "by custom env.py scripts"))
def mdowngrade(directory=None, revision='-1', sql=False, tag=None, x_arg=None):

    downgrade(directory=None, revision='-1', sql=False, tag=None, x_arg=None)


@MyMigrateCommand.option('revision', nargs='?', default="head",
                         help="revision identifier")
@MyMigrateCommand.option('-d', '--directory', dest='directory', default=None,
                         help=("migration script directory (default is "
                               "'migrations')"))
def mshow(directory=None, revision='head'):

    show(directory=None, revision='head')


@MyMigrateCommand.option('-v', '--verbose', dest='verbose', action='store_true',
                         default=False, help='Use more verbose output')
@MyMigrateCommand.option('-r', '--rev-range', dest='rev_range', default=None,
                         help='Specify a revision range; format is [start]:[end]')
@MyMigrateCommand.option('-d', '--directory', dest='directory', default=None,
                         help=("migration script directory (default is "
                               "'migrations')"))
def mhistory(directory=None, rev_range=None, verbose=False):

    history(directory=None, rev_range=None, verbose=False)


@MyMigrateCommand.option('--resolve-dependencies', dest='resolve_dependencies',
                         action='store_true', default=False,
                         help='Treat dependency versions as down revisions')
@MyMigrateCommand.option('-v', '--verbose', dest='verbose', action='store_true',
                         default=False, help='Use more verbose output')
@MyMigrateCommand.option('-d', '--directory', dest='directory', default=None,
                         help=("migration script directory (default is "
                               "'migrations')"))
def mheads(directory=None, verbose=False, resolve_dependencies=False):
    heads(directory=None, verbose=False, resolve_dependencies=False)


@MyMigrateCommand.option('-v', '--verbose', dest='verbose', action='store_true',
                         default=False, help='Use more verbose output')
@MyMigrateCommand.option('-d', '--directory', dest='directory', default=None,
                         help=("migration script directory (default is "
                               "'migrations')"))
def mbranches(directory=None, verbose=False):
    branches(directory=None, verbose=False)


@MyMigrateCommand.option('--head-only', dest='head_only', action='store_true',
                         default=False,
                         help='Deprecated. Use --verbose for additional output')
@MyMigrateCommand.option('-v', '--verbose', dest='verbose', action='store_true',
                         default=False, help='Use more verbose output')
@MyMigrateCommand.option('-d', '--directory', dest='directory', default=None,
                         help=("migration script directory (default is "
                               "'migrations')"))
def mcurrent(directory=None, verbose=False, head_only=False):

    current(directory=None, verbose=False, head_only=False)


@MyMigrateCommand.option('--tag', dest='tag', default=None,
                         help=("Arbitrary 'tag' name - can be used by custom "
                               "env.py scripts"))
@MyMigrateCommand.option('--sql', dest='sql', action='store_true', default=False,
                         help=("Don't emit SQL to database - dump to standard "
                               "output instead"))
@MyMigrateCommand.option('revision', default=None, help="revision identifier")
@MyMigrateCommand.option('-d', '--directory', dest='directory', default=None,
                         help=("migration script directory (default is "
                               "'migrations')"))
def mstamp(directory=None, revision='head', sql=False, tag=None):
    stamp(directory=None, revision='head', sql=False, tag=None)