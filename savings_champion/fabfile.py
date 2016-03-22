from fabric.context_managers import cd
from fabric.contrib.files import exists
from fabric.decorators import task
from fabric.operations import run, sudo
from fabric.state import env
from fabtools import require, supervisor, deb, python
from fabtools.python import virtualenv


env.roledefs = {
    'master': ['savingschampion@savingschampion.co.uk'],
    'develop': ['savingschampion@preview.savingschampion.co.uk'],
    #'concierge_engine': ['savingschampion@preview.savingschampion.co.uk'],
    'vagrant': ['savingschampion@127.0.0.1:2222']
}

NGINX_NOSSL_CONFIG = '''
server {
    listen         %(port)d default_server;
    expires    24h;
    return 301 https://$host$request_uri;
}
'''

NGINX_SSL_PRODUCTION_CONFIG = '''
server {
    listen               %(port)d ssl;
    server_name          %(server_name)s %(server_alias)s;
    access_log           /var/log/nginx/%(server_name)s.log;
    ssl_certificate      %(doc_root)s/%(ssl_certificate)s;
    ssl_certificate_key  %(doc_root)s/%(ssl_key)s;

    ssl_prefer_server_ciphers On;
    ssl_protocols SSLv3 TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS;

    #HTTP Strict Transport Security
    #add_header Strict-Transport-Security "max-age=30; includeSubDomains";
    #add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    client_max_body_size 10M;
    # Gzip configuration
    gzip on;
    gzip_static on;
    gzip_disable "MSIE [1-6]\.(?!.*SV1)";

    gzip_vary on;
    gzip_comp_level 6;
    gzip_buffers 16 8k;
    gzip_http_version 1.1;

    # don't gzip images, woff
    gzip_types text/plain text/css application/json application/x-javascript text/xml application/xml application/xml+rss text/javascript application/javascript text/x-js font/ttf font/opentype application/vnd.ms-fontobject image/svg+xml;

try_files $uri @proxied;

location @proxied {
    uwsgi_pass unix://%(proxy_url)s;
    uwsgi_read_timeout 300;
    include uwsgi_params;
}

location /static {
    expires 1y;
    alias %(static_path)s;
}

location /assets {
    expires 1y;
    alias %(media_path)s;
}

}
'''

NGINX_SSL_PREVIEW_CONFIG = '''
server {
    listen               %(port)d ssl;
    server_name          %(server_name)s %(server_alias)s;
    access_log           /var/log/nginx/%(server_name)s.log;
    auth_basic "Restricted";
    auth_basic_user_file %(doc_root)s/.htaccess;
    ssl_certificate      %(doc_root)s/%(ssl_certificate)s;
    ssl_certificate_key  %(doc_root)s/%(ssl_key)s;

    ssl_prefer_server_ciphers On;
    ssl_protocols SSLv3 TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS;

    #HTTP Strict Transport Security
    #add_header Strict-Transport-Security "max-age=30; includeSubDomains";
    #add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    client_max_body_size 10M;
    # Gzip configuration
    gzip on;
    gzip_static on;
    gzip_disable "MSIE [1-6]\.(?!.*SV1)";

    gzip_vary on;
    gzip_comp_level 6;
    gzip_buffers 16 8k;
    gzip_http_version 1.1;

    # don't gzip images, woff
    gzip_types text/plain text/css application/json application/x-javascript text/xml application/xml application/xml+rss text/javascript application/javascript text/x-js font/ttf font/opentype application/vnd.ms-fontobject image/svg+xml;

try_files $uri @proxied;

location @proxied {
    uwsgi_pass unix://%(proxy_url)s;
    uwsgi_read_timeout 300;
    include uwsgi_params;
}

location /static {
    expires 1y;
    alias %(static_path)s;
}

location /assets {
    expires 1y;
    alias %(media_path)s;
}

}
'''

VIRTUALENV_PATH = '/home/savingschampion/.virtualenv/savings_champion'
PROJECT_PATH = '/srv/www/savings_champion/savings_champion'
UWSGI_PATH = '/tmp/uwsgi.sock'

@task
def provision():
    project_path = '/srv/www/savings_champion/savings_champion'
    virtualenv_path = '/home/savingschampion/.virtualenv/savings_champion'
    require.files.directory('/srv/www/', use_sudo=True, owner='savingschampion', group='savingschampion')
    deb.update_index()
    require.postgres.server()
    require.deb.packages(['libpq-dev', 'memcached', 'libtiff4-dev', 'libjpeg8-dev', 'zlib1g-dev', 'libfreetype6-dev',
                          'liblcms1-dev', 'libwebp-dev'])
    require.postgres.user('savings_champion', 'r8Y@Mge#aTtW', createdb=True)
    require.postgres.database('savings_champion', 'savings_champion')

    require.python.virtualenv(virtualenv_path)
    require.python.packages(['uwsgi', 'flower'], use_sudo=True)
    require.files.directory('/var/log/uwsgi/', use_sudo=True)
    require.files.directory('/var/log/celeryd/', use_sudo=True)
    require.files.directory('/var/log/flower/', use_sudo=True)
    require.nodejs.installed_from_source()
    require.nodejs.package('yuglify')
    require.postfix.server('5.9.87.167')

    with virtualenv(virtualenv_path):
        python.install_requirements("/".join([project_path, 'requirements.txt']), upgrade=True, quiet=False)
        with cd('%s' % project_path):
            if not exists('settings.py'):
                run('ln -s settings_production.py settings.py')
            run('python manage.py collectstatic --noinput')
            run('python manage.py syncdb --noinput')
            run('python manage.py migrate')

    require.deb.package('rabbitmq-server')
    sudo('rabbitmqctl add_vhost guest')
    sudo('rabbitmqctl set_permissions -p guest guest ".*" ".*" ".*"')
    uwsgi_path = '/tmp/uwsgi.sock'
    with cd('%s' % project_path):

        require.supervisor.process('uwsgi',
                                   command="uwsgi --socket %s --master --workers 4 --home %s --chdir %s --file django.wsgi --harakiri=60 --reaper" % (
                                       uwsgi_path, virtualenv_path, project_path),
                                   directory=project_path, user='www-data',
                                   stdout_logfile='/var/log/uwsgi/savingschampion.log', stopsignal='QUIT')
        supervisor.restart_process('uwsgi')

        require.file('celerybeat-schedule.db', use_sudo=True, owner='www-data', group='www-data')

        for celery_pool in xrange(1, stop=3):
            require.supervisor.process('celery-%s' % celery_pool,
                                       command="%s/bin/celery worker -E -A celeryapp --concurrency=10 -n worker%s.localhost" % (virtualenv_path, celery_pool),
                                       directory=project_path, user='savingschampion',
                                       stdout_logfile='/var/log/celeryd/savingschampion.log', redirect_stderr=True,
                                       environment='DJANGO_SETTINGS_MODULE=settings')

        supervisor.restart_process('celery')

        require.nginx.server()
        require.nginx.disable('default')
        require.nginx.site('savings_champion', template_contents=NGINX_NOSSL_CONFIG, enabled=True, check_config=True,
                           port=80)
        require.nginx.site('savings_champion_ssl', template_contents=NGINX_SSL_PRODUCTION_CONFIG, enabled=True,
                           check_config=True,
                           port=443, server_alias='savingschampion.co.uk', doc_root=project_path, proxy_url=uwsgi_path,
                           static_path='/'.join([project_path, '..', 'static']),
                           media_path='/'.join([project_path, 'assets']),
                           ssl_certificate='www_savingschampion_co_uk.cert', ssl_key='www_savingschampion_co_uk.key')

        require.supervisor.process('flower',
                                   command="flower --broker=amqp://guest@localhost:5672// --address=0.0.0.0 --basic_auth=savingschampion:Over9000!",
                                   stdout_logfile='/var/log/flower/savingschampion.log', redirect_stderr=True,
                                   user="www-data")


@task
def update():

    git()
    _virtualenv()
    with cd('%s' % PROJECT_PATH):
        if not exists('settings.py'):
            run('ln -s settings_production.py settings.py')
    static(no_git=True)
    database()
    code(no_git=True, no_venv=True)
    nginx()


@task
def git():
    for key, value in env.roledefs.iteritems():
        if env.host_string in value:
            require.git.working_copy('git@git.assembla.com:savings-champion.git', path='/srv/www/savings_champion',
                                     update=True, branch=key)
            break
    else:
        require.git.working_copy('git@git.assembla.com:savings-champion.git', path='/srv/www/savings_champion',
                                 update=True)


@task
def html():
    git()


@task
def static(no_git=False):
    if not no_git:
        git()
    with virtualenv(VIRTUALENV_PATH):
        with cd('%s' % PROJECT_PATH):
            run('python manage.py collectstatic --noinput')

@task
def css():
    static()


@task
def images():
    static()


@task
def database(*args):
    require.postgres.server()
    require.deb.packages(['libpq-dev'])
    require.postgres.user('savings_champion', 'r8Y@Mge#aTtW', createdb=True)
    require.postgres.database('savings_champion', 'savings_champion')
    with virtualenv(VIRTUALENV_PATH):
        with cd('%s' % PROJECT_PATH):
            run('python manage.py syncdb --noinput')
            for app in args:
                try:
                    run('python manage.py schemamigration %s --auto' % app)
                except:
                    run('python manage.py schemamigration %s --initial' % app)
                    run('python manage.py migrate --fake')
            run('python manage.py migrate --merge')


@task
def uwsgi():
    supervisor.restart_process('uwsgi')


@task
def celery():
    supervisor.restart_process('celery')
    supervisor.restart_process('celery-1')
    supervisor.restart_process('celery-2')
    supervisor.restart_process('celery-3')


@task
def _virtualenv():
    with virtualenv(VIRTUALENV_PATH):
        python.install_requirements('/'.join([PROJECT_PATH, 'requirements.txt']), upgrade=True, quiet=False)

@task
def code(no_git=False, no_venv=False):
    if not no_git:
        git()
    if not no_venv:
        _virtualenv()
    celery()
    uwsgi()


@task
def nginx():
    require.nginx.site('savings_champion', template_contents=NGINX_NOSSL_CONFIG, enabled=True, check_config=True,
                       port=80)

    for key, value in env.roledefs.iteritems():
        if env.host_string in value:
            if key == 'master':
                require.nginx.site('savings_champion_ssl', template_contents=NGINX_SSL_PRODUCTION_CONFIG, enabled=True,
                                   check_config=True,
                                   port=443, server_alias='savingschampion.co.uk', doc_root=PROJECT_PATH,
                                   proxy_url=UWSGI_PATH,
                                   static_path='/'.join([PROJECT_PATH, '..', 'static']),
                                   media_path='/'.join([PROJECT_PATH, 'assets']),
                                   ssl_certificate='wildcard_savingschampion_co_uk.crt',
                                   ssl_key='wildcard_savingschampion_co_uk.key')
            else:
                require.nginx.site('savings_champion_ssl', template_contents=NGINX_SSL_PREVIEW_CONFIG, enabled=True,
                                   check_config=True,
                                   port=443, server_alias='savingschampion.co.uk', doc_root=PROJECT_PATH,
                                   proxy_url=UWSGI_PATH,
                                   static_path='/'.join([PROJECT_PATH, '..', 'static']),
                                   media_path='/'.join([PROJECT_PATH, 'assets']),
                                   ssl_certificate='wildcard_savingschampion_co_uk.crt',
                                   ssl_key='wildcard_savingschampion_co_uk.key')