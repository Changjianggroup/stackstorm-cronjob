from st2common.runners.base_action import Action
from st2client.client import Client
from st2client.models import KeyValuePair
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.rdbms.mysql import MySQLManagementClient
from azure.mgmt.rdbms.postgresql import PostgreSQLManagementClient
from azure.mgmt.sql import SqlManagementClient
import datetime
class AzureDeleteDBserverFirewallRuleAction(Action):
  def run(self,list_subscription_name,list_dbserver_type,subscription_id,client_id,client_tenant):
    list_result = list()
    for subscription_name in list_subscription_name:
      print subscription_name
      for dbserver_type in list_dbserver_type:
        print dbserver_type
        subscriptionid = subscription_id[subscription_name]
        client = Client(base_url='http://localhost')
	client_secret = client.keys.get_by_name(name='azure_stackstorm_secret', decrypt=True)
        credentials = ServicePrincipalCredentials(client_id, client_secret.value, tenant=client_tenant, china=True)
        if dbserver_type == "mysql":
          dbserverclient = MySQLManagementClient(credentials, subscriptionid, base_url="https://management.chinacloudapi.cn")
        if dbserver_type == "postgresql":
          dbserverclient = PostgreSQLManagementClient(credentials, subscriptionid, base_url="https://management.chinacloudapi.cn")
        if dbserver_type == "sqlserver":
          dbserverclient = SqlManagementClient(credentials, subscriptionid, base_url="https://management.chinacloudapi.cn") 
        list_dict_resgroup_dbserver = self._list_all_dbserverserver(dbserverclient)
        num = len(list_dict_resgroup_dbserver)
        for n in range(0, num):
          dict_resgroup_rules = dict()
          list_rule =self._list_firewall_rule(dbserverclient,list_dict_resgroup_dbserver[n]["resource_group"],list_dict_resgroup_dbserver[n]["dbserver_name"])
          dict_resgroup_rules["resource_group"] = list_dict_resgroup_dbserver[n]["resource_group"]
          dict_resgroup_rules["dbserver_name"] = list_dict_resgroup_dbserver[n]["dbserver_name"]
          dict_resgroup_rules["rule_name"] = list_rule
          now_time = datetime.datetime.now().strftime("%y-%m-%d")
          rule_num = len(dict_resgroup_rules["rule_name"])
          for i in range(0, rule_num):
            if dict_resgroup_rules["rule_name"][i].split('_')[0] == now_time:
              result = self._delete_rule(dbserverclient,dict_resgroup_rules["resource_group"],dict_resgroup_rules["dbserver_name"],dict_resgroup_rules["rule_name"][i])
              list_result.append(result)
    return (True,list_result)
  def _list_firewall_rule(self, dbserverclient, resource_group, dbserver_name):
    rule_page = dbserverclient.firewall_rules.list_by_server(resource_group, dbserver_name)
    list_rule = list()
    for i in rule_page:
      rule = str(i)
      try:
      	res1 = rule.split("'name': u'")[1]
      	rule_name = res1.split("', '")[0]
      	list_rule.append(rule_name)
      except IndexError:
        pass
    return list_rule
  def _list_all_dbserverserver(self, dbserverclient):
    dbserverserver_page = dbserverclient.servers.list()
    list_dict_resgroup_dbserver = list()
    for i in dbserverserver_page:
      dict_resgroup_dbservername = dict()
      res1 = str(i)
      id = res1.split("'id': u'/subscriptions")[1]
      res2 = id.split('/')
      resourcegroup = res2[3]
      dbservername = res2[7].split("'")[0]
      dict_resgroup_dbservername["resource_group"] = resourcegroup
      dict_resgroup_dbservername["dbserver_name"] = dbservername
      list_dict_resgroup_dbserver.append(dict_resgroup_dbservername)
    return list_dict_resgroup_dbserver
  def _delete_rule(self, dbserverclient, resource_group, dbserver_name, rule_name):
    try:
      res = dbserverclient.firewall_rules.delete(resource_group, dbserver_name, rule_name)
      return res
    except Exception as e:
      return e.message
#                                        
