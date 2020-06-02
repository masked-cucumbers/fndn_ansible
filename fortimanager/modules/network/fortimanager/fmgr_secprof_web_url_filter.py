#!/usr/bin/python
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'metadata_version': '1.1'}

DOCUMENTATION = '''
---
module: fmgr_secprof_web
version_added: "2.8"
notes:
    - Full Documentation at U(https://ftnt-ansible-docs.readthedocs.io/en/latest/).
author:
    - Pierre-Alain CRUTCHET
short_description: Manage web URL filter in FortiManager
description:
  -  Manage web URL filter in FortiManager through playbooks using the FMG API

options:
  adom:
    description:
      - The ADOM the configuration should belong to.
    required: false
    default: root

  mode:
    description:
      - Sets one of three modes for managing the object.
      - Allows use of soft-adds instead of overwriting existing values
    choices: ['get', 'add', 'set', 'delete', 'update']
    required: false
    default: get
  
  comment:
    description:
      - Optional comments.
    required: false
  
  name:
    description:
      - Name of the web url filter
      - If specified with get mode, the result returned will only contain the web url list having an exact match on the name field
    required: false
    
  id:
    description:
      - Id of the web url filter
      - If specified with get mode, the result returned is the web url filter with the specified id 
    required: false
  
  one_arm_ips_urlfilter:
    description:
      - Enable/disable DNS resolver for one-arm IPS URL filter operation.
      - choice | disable | Disable setting.
      - choice | enable | Enable setting.
    required: false
    choices: ["disable", "enable"]
  
  ip-addr-block:
    description:
      - Enable/disable blocking URLs when the hostname appears as an IP address.
      - choice | disable | Disable setting.
      - choice | enable | Enable setting.
    required: false
    choices: ["disable", "enable"]
  
  entries:
    description:
      - EXPERTS ONLY! KNOWLEDGE OF FMGR JSON API IS REQUIRED!
      - List of multiple child objects to be added. Expects a list of dictionaries.
      - Dictionaries must use FortiManager API parameters, not the ansible ones listed below.
      - If submitted, all other prefixed sub-parameters ARE IGNORED.
      - This object is MUTUALLY EXCLUSIVE with its options.
      - We expect that you know what you are doing with these list parameters, and are leveraging the JSON API Guide.
      - WHEN IN DOUBT, USE THE SUB OPTIONS BELOW INSTEAD TO CREATE OBJECTS WITH MULTIPLE TASKS
    required: false
  
  
'''

EXAMPLES = '''
- name: update webfilter URL list
  hosts: Fortimanager
  connection: httpapi
  gather_facts: no
  tasks:
    - name: display target webfilter and save result
      fmgr_secprof_web_url_filter:
        adom: "{{ adom }}"
        mode: "get"
        name: "{{webfilter}}"
      register: result

    - name: import webfilter param from a file
      include_vars:
        dir: /path/to/webfilters/
        files_matching: "{{webfilter}}.yml"
        name: webfilter_param

    - name: add or update the webfilter
      fmgr_secprof_web_url_filter:
        adom: "{{ adom }}"
        mode: "set"
        id: "{{result.results.0.id}}"
        name: "{{webfilter_param.name}}"
        one_arm_ips_urlfilter: "{{webfilter_param.one_arm_ips_urlfilter}}"
        ip_addr_block: "{{webfilter_param.ip_addr_block}}"
        entries: "{{ webfilter_param.entries }}"
'''

RETURN = """
api_result:
  description: full API response, includes status code and message
  returned: always
  type: str
"""

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible.module_utils.connection import Connection
from ansible.module_utils.network.fortimanager.fortimanager import FortiManagerHandler
from ansible.module_utils.network.fortimanager.common import FMGBaseException
from ansible.module_utils.network.fortimanager.common import FMGRCommon
from ansible.module_utils.network.fortimanager.common import FMGRMethods
from ansible.module_utils.network.fortimanager.common import DEFAULT_RESULT_OBJ
from ansible.module_utils.network.fortimanager.common import FAIL_SOCKET_MSG
from ansible.module_utils.network.fortimanager.common import prepare_dict
from ansible.module_utils.network.fortimanager.common import scrub_dict


def fmgr_web_url_filter(fmgr, paramgram):

    mode = paramgram["mode"]
    adom = paramgram["adom"]

    response = DEFAULT_RESULT_OBJ
    url = ""
    datagram = {}

    # EVAL THE MODE PARAMETER FOR SET OR ADD
    if mode in ['set', 'add', 'update']:
        url = '/pm/config/adom/{adom}/obj/webfilter/urlfilter'.format(adom=adom)
        datagram = scrub_dict(prepare_dict(paramgram))

    # EVAL THE MODE PARAMETER FOR DELETE
    elif mode == "delete":
        # SET THE CORRECT URL FOR DELETE
        url = '/pm/config/adom/{adom}/obj/webfilter/urlfilter/{id}'.format(adom=adom, id=paramgram["id"])
        datagram = {}

    elif mode == "get" and paramgram["id"] is not None:
        url = '/pm/config/adom/{adom}/obj/webfilter/urlfilter/{id}'.format(adom=adom, id=paramgram["id"])
        datagram = {}
    elif mode == "get" and paramgram["name"] is not None:
        url = '/pm/config/adom/{adom}/obj/webfilter/urlfilter'.format(adom=adom)
        paramgram["filter"] = ["name", "==", paramgram["name"]]
        datagram = scrub_dict(prepare_dict(paramgram))
    elif mode == "get":
        url = '/pm/config/adom/{adom}/obj/webfilter/urlfilter'.format(adom=adom)
        datagram = {}

    response = fmgr.process_request(url, datagram, paramgram["mode"])

    return response


#############
# END METHODS
#############


def main():
    argument_spec = dict(
        adom=dict(type="str", default="root"),
        mode=dict(choices=["get", "add", "set", "delete", "update"], type="str", default="get"),
        filter=dict(required=False, type="list"),

        id=dict(required=False, type="str"),
        name=dict(required=False, type="str"),
        one_arm_ips_urlfilter=dict(required=False, type="str", choices=["disable", "enable"]),
        ip_addr_block=dict(required=False, type="str", choices=["disable", "enable"]),
        comment=dict(required=False, type="str"),
        entries=dict(required=False, type="list"),
        entries_id=dict(required=False, type="int"),
        entries_action=dict(required=False, type="str", choices=["allow", "block", "exempt", "monitor"]),
        entries_entries_dns_address_family=dict(required=False, type="str", choices=["both", "ipv4", "ipv6"]),
        entries_status=dict(required=False, type="str", choices=["enable", "disable"]),
        entries_type=dict(required=False, type="str", choices=["regex", "simple", "wildcard"]),
        entries_url=dict(required=False, type="str"),
        entries_web_proxy_profile=dict(required=False, type="list"),
        entries_referrer_host=dict(required=False, type="str"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False, )
    # MODULE PARAMGRAM
    paramgram = {
        "mode": module.params["mode"],
        "adom": module.params["adom"],
        "filter": module.params["filter"],
        "name": module.params["name"],
        "id": module.params["id"],
        "one-arm-ips-urlfilter": module.params["one_arm_ips_urlfilter"],
        "ip-addr-block": module.params["ip_addr_block"],
        "comment": module.params["comment"],
        "entries": {
            "id": module.params["entries_id"],
            "action": module.params["entries_action"],
            "dns-address-family": module.params["entries_entries_dns_address_family"],
            "status": module.params["entries_status"],
            "type": module.params["entries_type"],
            "url": module.params["entries_url"],
            "web-proxy-profile": module.params["entries_web_proxy_profile"],
            "referrer-host": module.params["entries_referrer_host"]
        },
    }
    module.paramgram = paramgram
    fmgr = None
    if module._socket_path:
        connection = Connection(module._socket_path)
        fmgr = FortiManagerHandler(connection, module)
        fmgr.tools = FMGRCommon()
    else:
        module.fail_json(**FAIL_SOCKET_MSG)

    list_overrides = ['entries']
    paramgram = fmgr.tools.paramgram_child_list_override(list_overrides=list_overrides,
                                                         paramgram=paramgram, module=module)

    results = DEFAULT_RESULT_OBJ

    try:

        results = fmgr_web_url_filter(fmgr, paramgram)
        fmgr.govern_response(module=module, results=results,
                             ansible_facts=fmgr.construct_ansible_facts(results, module.params, paramgram))

    except Exception as err:
        raise FMGBaseException(err)

    return module.exit_json(**results[1])


if __name__ == "__main__":
    main()
