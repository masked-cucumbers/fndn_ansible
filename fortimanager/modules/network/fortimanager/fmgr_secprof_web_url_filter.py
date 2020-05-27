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
'''

EXAMPLES = '''
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
        url = '/pm/config/adom/{adom}/obj/webfilter/urlfilter/{name}'.format(adom=adom, name=paramgram["name"])
        datagram = {}

    elif mode == "get" and "id" in paramgram:
        url = '/pm/config/adom/{adom}/obj/webfilter/urlfilter/{id}'.format(adom=adom,id=paramgram["id"])
        datagram = {}
    elif mode == "get" and "name" in paramgram:
        url = '/pm/config/adom/{adom}/obj/webfilter/urlfilter'.format(adom=adom)
        paramgram["filter"] = [ "name", "==", paramgram["name"]]
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
