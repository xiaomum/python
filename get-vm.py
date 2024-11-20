# -*- coding: utf-8 -*-
import requests
from com.vmware.cis_client import Session
from vmware.vapi.lib.connect import get_requests_connector
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from vmware.vapi.security.session import create_session_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory
from vmware.vapi.security.user_password import \
    create_user_password_security_context

server = '10.211.93.236'
username = 'test'
password = '*IK<0okm'
skip_verification = True
host_url = 'https://{server}/api'

session = requests.Session()
session.verify = False
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
connector = get_requests_connector(session=session, url=host_url)
stub_config = StubConfigurationFactory.new_std_configuration(connector)
user_password_security_context = create_user_password_security_context(username,
                                                                       password)
stub_config.connector.set_security_context(user_password_security_context)
session_svc = Session(stub_config)
session_id = session_svc.create()
session_security_context = create_session_security_context(session_id)
stub_config.connector.set_security_context(session_security_context)
