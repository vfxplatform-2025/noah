# -*- coding: utf-8 -*-

name = 'noah'

version = '2.0.0'

description = 'Noah deault settings'

authors = ['M83 noah']

plugin_for = ['maya']

build_requires = ['python-2']

def commands():
    env.noah_major = "2"
    env.noah_minor = "0"
    env.noah_rev = "0"
    env.noah_version="noah-v{0}.{1}.{2}".format(env.noah_major, env.noah_minor, env.noah_rev)
    env.NOAH_ROOT="{this.root}"
    env.PATH.append("{this.root}")
    #env.PYTHONPATH.append("/core/Linux/APPZ/Python/2.7/lib/python2.7/site-packages")
    env.PYTHONPATH.append("{this.root}")
    env.XBMLANGPATH.append("{this.root}/icon/%B")

uuid = '3d.noah_exec'

timestamp = 1701932596

changelog = \
    """
    commit 00c1983deb1c798505ef95757676078e92a903e0
    Merge: e21dbc7 c62cb81
    Author: chulho jung <chulho@m83.co.kr>
    Date:   Thu Dec 7 06:02:53 2023 +0000
    
        Merge branch 'jiho' into 'main'
    
        noah in maya2024 and rockyOS
    
        See merge request rez/noah!2
    
    commit c62cb813641a6226e99bc242e309f3c26fff2a69
    Author: jiho <jiho@m83.co.kr>
    Date:   Thu Dec 7 15:38:33 2023 +0900
    
        noah in maya2024 and rockyOS
    
    commit e21dbc793e6d9fedc56cca8d55723edf2bd1baf5
    Merge: f6afb88 5b4a746
    Author: jiho yang <jiho@m83.co.kr>
    Date:   Thu Dec 7 05:09:06 2023 +0000
    
        Merge branch 'jiho' into 'main'
    
        cent7 noah
    
        See merge request rez/noah!1
    
    commit 5b4a7463a14023a2ded413722b668696edbf3ef4
    Author: jiho <jiho@m83.co.kr>
    Date:   Thu Dec 7 14:45:12 2023 +0900
    
        cent7 noah
    
    commit f6afb88ad2ad81e2831e9f1296c9a4070a241a0b
    Author: jiho yang <jiho@m83.co.kr>
    Date:   Thu Dec 7 05:05:15 2023 +0000
    
        Initial commit
    """

vcs = 'git'

revision = \
    {'branch': 'main',
     'commit': '00c1983deb1c798505ef95757676078e92a903e0',
     'fetch_url': 'git@192.168.10.14:rez/noah.git',
     'push_url': 'git@192.168.10.14:rez/noah.git',
     'tracking_branch': 'origin/main'}

format_version = 2
