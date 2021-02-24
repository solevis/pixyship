import time
from contextlib import contextmanager

from fabric.api import env, put, run, runs_once, prefix, cd, local, sudo
from fabric.colors import red, green
from fabric.context_managers import lcd, warn_only, hide
from fabric.contrib.files import append, exists
from fabric.exceptions import CommandTimeout
from fabric.operations import get

from data_load import update_data as db_update_data

APT_PACKAGES = (
    'build-essential '
    'libssl-dev '
    'libffi-dev '
    'python-dev '
    'python3-pip '
    'htop '
    'dtach '
    'docker-ce'
)

# Your repo goes here
REPO = 'git@github.com:JThinkable/pixyship.git'

# copy this from your .ssh folder to the local directory
GIT_KEY = 'pixyship_deploy'

env.use_ssh_config = True

# Default environment (Dev) settings
env.name = 'Development'
env.config_file = 'config/dev.cfg'
env.alembic_file = 'config/alembic_dev.ini'
env.in_cloud = False
env.alembic_upgrade = 'alembic upgrade head'
if not hasattr(env, 'base_name'):
    env.base_name = 'pixyship'
env.src_dir = 'src/' + env.base_name
env.venv = env.base_name + '_env'


def lightsail():
    env.alembic_file = 'config/alembic_ls.ini'
    env.hosts = ['pixy-ls']


def ls():
    env.alembic_file = 'config/alembic_ls.ini'


@contextmanager
def virtualenv(env_dir):
    # env_dir is the path to the venv from the home directory
    with prefix('source ~/{}/bin/activate'.format(env_dir)):
        yield


def runbg(cmd, sockname="dtach"):
    return run('dtach -n `mktemp -u /tmp/%s.XXXX` %s' % (sockname, cmd))


# Environment definitions -----------------------------------------------------
env.git_branch = 'master'


# Commands --------------------------------------------------------------------
def debug():
    print(env)


def update_data():
    """Update local data"""
    db_update_data()


@runs_once
def deploy():
    stop_worker()
    deploy_web()
    start_worker()


def _deploy_base():
    sudo('apt update', shell=False)
    sudo('apt -y install ' + APT_PACKAGES, shell=False)
    with cd(env.src_dir):
        # Force branch to the head of it's branch from the server, in case the
        # server was force pushed
        run('git fetch && git reset --hard FETCH_HEAD')
        with virtualenv(env.venv):
            migrate_database()
            run('pip3 install -r requirements.txt')


def restart_web():
    """Restart the web server"""
    # This can be called with just a host arg
    with virtualenv(env.venv), cd(env.src_dir):
        sudo('service nginx stop')
        run('pkill uwsgi ||:')
        sudo('cp config/pixstar /etc/nginx/sites-available/')
        runbg('uwsgi --ini uwsgi.ini -b 32768')
        sudo('service nginx restart')


def deploy_web():
    """Updates web to the head of it's current branch"""
    # This can be called with just a host arg
    build_ui()
    _deploy_base()
    with virtualenv(env.venv), cd(env.src_dir):
        sudo('service nginx stop')
        run('pkill uwsgi ||:')
        sudo('cp config/pixstar /etc/nginx/sites-available/')

        put('dist', '~/' + env.src_dir)

        runbg('uwsgi --ini uwsgi.ini -b 32768')
        sudo('service nginx restart')


def restart():
    with virtualenv(env.venv), cd(env.src_dir):
        sudo('service nginx stop')
        run('pkill uwsgi ||:')
        runbg('uwsgi --ini uwsgi.ini -b 32768')
        sudo('service nginx restart')


@runs_once
def migrate_database():
    # Only run alembic update on a single worker
    run('cp {} alembic.ini'.format(env.alembic_file))
    run(env.alembic_upgrade)


@runs_once
def setup():
    setup_web()


@runs_once
def setup_web():
    _setup_base()
    with cd('src'):
        sudo('apt -y install nginx')
        sudo('pwd')
        sudo('cp pixyship/config/pixstar /etc/nginx/sites-available/')
        sudo('ln -sf ../sites-available/pixstar /etc/nginx/sites-enabled/')
        sudo('rm -f /etc/nginx/sites-enabled/default')
        sudo('mkdir -p /var/log/uwsgi')
        sudo('chown -R ubuntu:adm /var/log/uwsgi')

    with cd(env.src_dir), virtualenv(env.venv):
        migrate_database()
        run('fab update_data')

    return env.host_string


@runs_once
def _setup_base():
    try:
        append('.bashrc', '. ~/{}/bin/activate'.format(env.venv))

        # Docker CE repo
        # TODO Parameterize local postgres
        sudo('curl -fsSL https://download.docker.com/linux/ubuntu/gpg | '
             'sudo apt-key add -')
        sudo('sudo add-apt-repository '
             '"deb [arch=amd64] https://download.docker.com/linux/ubuntu '
             '$(lsb_release -cs) stable"')
        # -c 512 is 50% of 1024 cpu units (maybe?)
        # Update packages, ensure installation
        sudo('apt update')
        sudo('apt -y install ' + APT_PACKAGES)

        images_out = sudo('docker ps -a -q')
        # images = images_out.splitlines()
        # for i in images:
        #     sudo('docker rm -f ' + i)
        if not images_out:
            sudo('docker run -c 512 -p 5433:5432 --name postgres -e POSTGRES_'
                 'PASSWORD=password -d postgres')

        # Configure git access
        put(GIT_KEY, '.ssh/', mode=0o600)
        put('deploy_ssh_config', '.ssh/config')

        # Grab code
        run('mkdir -p src')
        # Get the repo origin URL from deploy repo
        # repo_url = local('git config --get remote.origin.url', capture=True)
        if not exists(env.src_dir):
            with cd('src'):
                # run('ssh -o StrictHostKeyChecking=no git@github.com')
                run('git clone ' + REPO)
        with cd(env.src_dir):
            run('git checkout ' + env.git_branch)
            run('git pull')

        # Install environment
        run('pip3 install virtualenv')
        run('virtualenv -p python3 ~/{}'.format(env.venv))

        # Install python requirements
        with cd(env.src_dir), virtualenv(env.venv):
            run('pip3 install -r requirements.txt')

    except ValueError as e:
        if "local path" in str(e):
            print(e)
            print("Make sure the '.pem' ssh key is in your service directory")


def stop_worker():
    # Workers need to run continuous processes w/ Circus
    with virtualenv(env.venv), cd(env.src_dir):
        run('circusd --daemon --log-level debug --log-output circus.log '
            'config/circus.ini')
        try:
            run('circusctl stop', timeout=5)
        except CommandTimeout:
            print('circus reload timed out')


def start_worker():
    # Workers need to run continuous processes w/ Circus
    with virtualenv(env.venv), cd(env.src_dir):
        run('circusd --daemon --log-level debug --log-output circus.log '
            'config/circus.ini')
        try:
            run('circusctl start', timeout=5)
        except CommandTimeout:
            print('circus reload timed out')


# Docker DB commands
def get_prod_data(pw=None, host=None):
    # Load data from an existing, available source, or just reload it.
    if pw and host:
        import_db(pw, host)
    drop_tables()
    load_data()


def import_db(pw, host):
    # This gets and downloads a dump from the target host db
    sudo(
        'docker exec postgres bash -c "PGPASSWORD={pw} pg_dump -h {host} '
        '-U pixymaster -f dump.sql postgres"'.format(pw=pw, host=host)
    )


def load_data():
    sudo('docker exec ps_postgres psql -U postgres -f dump.sql')


def download_db():
    run('docker exec postgres pg_dump -U postgres -f backup.sql postgres')
    run('docker cp postgres:/backup.sql .')
    run('gzip -f backup.sql')
    get('backup.sql.gz')


def load_local_data():
    # Load data into the local postgres environment.  Drop existing tables first.
    local('docker cp pixy-ls/backup.sql ps_postgres:/dump.sql')
    local('docker exec ps_postgres psql -U postgres -f dump.sql')


def drop_tables():
    res = sudo('PGPASSWORD=password psql -t -h localhost -U postgres -c '
               '"SELECT tablename FROM pg_tables '
               'WHERE schemaname = \'public\'"')
    tables = [line.strip() for line in res.splitlines()]
    for table in tables:
        print(table)
        sudo('PGPASSWORD=password psql -t -h localhost '
             '-U postgres -c "DROP TABLE {} CASCADE"'.format(table))


# Dev Environment commands ----------------------------------------------------
def init_dev():
    # local('virtualenv venv')
    # local(r'venv\scripts\activate & pip install -r dev_reqs.txt')
    print(r'Activate the virtual environment venv\scripts\activate')


def lint():
    with warn_only(), hide('warnings'):
        res = local('pycodestyle .')
    print('lint ', end='')
    if res.failed:
        print(red('failed'))
    else:
        print(green('passed'))


def create_postgres():
    local('docker run -p 5433:5432 --name ps_postgres -e POSTGRES_'
          'PASSWORD=password -d postgres')
    print('Waiting for ps_postgres to start')
    time.sleep(10)
    local('alembic upgrade head')


def start_dockers():
    local('docker start ps_postgres')


def ui():
    with lcd('frontend'):
        local('npm run dev')


def npm_install():
    with lcd('frontend'):
        local('npm install')


def build_ui():
    with lcd('frontend'):
        local('npm run build')
