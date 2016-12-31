# -*- coding: utf-8 -*-
'''
Minion side functions for salt-cp
'''
from __future__ import absolute_import

# Import python libs
import os
import logging
import fnmatch

# Import salt libs
import salt.minion
import salt.fileclient
import salt.utils
import salt.crypt
import salt.transport
from salt.exceptions import CommandExecutionError

import os
import logging
import fnmatch
import json

# Import salt libs
import salt.minion
import salt.fileclient
import salt.utils
import salt.crypt
import salt.transport
from salt.exceptions import CommandExecutionError

def getJson(a,saltenv='base', template='jinja', **kw):
    if template:
        # render the path as a template using path_template_engine as the engine
        if template not in salt.utils.templates.TEMPLATE_REGISTRY:
            raise CommandExecutionError(
                'Attempted to render file paths with unavailable engine '
                '{0}'.format(template)
            )

        kwargs = {}
        kwargs['salt'] = __salt__
        if 'pillarenv' in kw or 'pillar' in kw:
            pillarenv = kw.get('pillarenv', __opts__.get('pillarenv'))
            kwargs['pillar'] = _gather_pillar(pillarenv, kw.get('pillar'))
        else:
            kwargs['pillar'] = __pillar__
        kwargs['grains'] = __grains__
        kwargs['opts'] = __opts__
        kwargs['saltenv'] = saltenv
        def _render(contents):
            '''
            Render :param:`contents` into a literal pathname by writing it to a
            temp file, rendering that file, and returning the result.
            '''
            # write out path to temp file
            tmp_path_fn = salt.utils.mkstemp()
            with salt.utils.fopen(tmp_path_fn, 'w+') as fp_:
                fp_.write(contents)
            data = salt.utils.templates.TEMPLATE_REGISTRY[template](
                tmp_path_fn,
                to_str=True,
                **kwargs
            )
            salt.utils.safe_rm(tmp_path_fn)
            if not data['result']:
                # Failed to render the template
                raise CommandExecutionError(
                    'Failed to render file path with error: {0}'.format(
                        data['data']
                    )
                )
            else:
                return data['data']
        a=_render(a)
    return a

def initMetastore(arg,cluster_name,user_name):
    metaStoreList=eval(getJson(arg))
    os.system("cp -f /software/servers/metastore-%s/.bashrc /home/%s/.bashrc" % (cluster_name,user_name)) 
    os.system("cp -r /software/servers/metastore-%s/hive_conf /software/conf/%s/ " % (cluster_name,user_name))
    os.system("cp -r /software/servers/metastore-%s/hadoop_conf /software/conf/%s/ " % (cluster_name,user_name))
    os.system("chown -R %s:%s /software/conf/%s/ /home/%s/.bashrc  "  % (user_name,user_name,user_name,user_name))
    os.system(" sed -i 's/{mysql_url}/%s/g' /software/conf/%s/hive_conf/hive-site.xml " % (metaStoreList['mysql_url'],user_name))
    os.system(" sed -i 's/{database_name}/%s/g' /software/conf/%s/hive_conf/hive-site.xml " % (metaStoreList['database_name'],user_name))
    os.system(" sed -i 's/{mysql_passwd}/%s/g' /software/conf/%s/hive_conf/hive-site.xml " % (metaStoreList['mysql_passwd'],user_name))
    os.system(" sed -i 's/{mysql_user}/%s/g' /software/conf/%s/hive_conf/hive-site.xml " % (metaStoreList['mysql_user'],user_name))
    os.system(" sed -i 's/{warehouse_dir}/%s/g' /software/conf/%s/hive_conf/hive-site.xml " % (metaStoreList['warehouse_dir'].replace('/','\/'),user_name))
    os.system(" sed -i 's/{cluster_id}/%s/g' /software/conf/%s/hive_conf/hive-site.xml " % (metaStoreList['cluster_id'],user_name))
    os.system(" sed -i 's/{authorization_enabled_final}/%s/g' /software/conf/%s/hive_conf/hive-site.xml " % (metaStoreList['authorization_enabled_final'],user_name))
    os.system(" sed -i s/{host_ip}/`hostname -i`/g /software/conf/%s/hive_conf/hive-site.xml " % user_name)
    os.system(" sed -i 's/{hive_version}/%s/g' /software/conf/%s/hive_conf/hive-site.xml " % (metaStoreList['hive_version'],user_name))
    os.system(" sed -i 's/{hive_version}/%s/g' /home/%s/.bashrc " % (metaStoreList['hive_version'],user_name))
    os.system(" sed -i 's/{metastore_port}/%s/g' /home/%s/.bashrc " % (metaStoreList['metastore_port'],user_name))
    return metaStoreList
