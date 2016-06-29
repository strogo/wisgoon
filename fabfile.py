from fabric.api import cd, run, local, env

env.hosts = ['79.127.125.104']
env.user = 'wisgoon'
env.use_ssh_config = True


def deploy():
    code_dir = '/home/wisgoon/new'
    local("git push new devel")

    with cd(code_dir):
        run("git merge devel")
        run("touch reload-new")


def cod():
    local('git add .')
    local('git commit -m "changein files"')
    deploy()
