from fabric.api import cd, run, local, env

env.hosts = ['79.127.125.104']
env.user = 'wisgoon'
env.password = 'O0k1.sgPACGgA'
env.use_ssh_config = True


def deploy():
    code_dir = '/home/wisgoon/new'
    try:
        local("git push new devel")
    except Exception, e:
        print str(e)

    with cd(code_dir):
        run("git merge devel")
        run("touch reload-new")


def cod():
    try:
        local('git add .')
        local('git commit -m "changein files"')
    except Exception, e:
        print str(e)
    deploy()
