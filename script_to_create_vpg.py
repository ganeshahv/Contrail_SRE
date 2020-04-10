import json
from vnc_api.vnc_api import *
from vnc_api import vnc_api
vh=VncApi(username=<username>,password=<password>,tenant_name='admin',api_server_host=<api_server_ip>,api_server_port='8082', auth_host=<auth_host>)
no_of_vns = 1
fabric_name=str('fabric1')
switch=str('r2ru39-qfx5100-leaf-2')
phy_intf=str('ge-0/0/2')
my_proj = vh.project_read(fq_name=[u'default-domain', u'admin'])
my_fab=vh.fabric_read(fq_name=[u'default-global-system-config', fabric_name])
my_sg=vh.security_group_read(fq_name=[u'default-domain', u'admin', u'default'])
my_ipam=vh.network_ipam_read(fq_name=[u'default-domain', u'default-project', u'default-network-ipam'])
my_pi=vh.physical_interface_read(fq_name=[u'default-global-system-config', str(switch), str(phy_intf)])
my_vn_ids=[]
my_vmi_ids=[]
tag_list = [1002]
print ("Creating %s VNs"%no_of_vns)
for i in range(1, no_of_vns+1):
    print ("Creating VN number %s"%i)
    vn_name = 'vn_' + str(i)
    ip_prefix = '193.168.' + str(i) + '.0'
    obj_0 = vnc_api.VirtualNetwork(name=vn_name,parent_obj=my_proj)
    obj_1 = vnc_api.VnSubnetsType()
    obj_2 = vnc_api.IpamSubnetType()
    obj_3 = vnc_api.SubnetType()
    obj_3.set_ip_prefix(ip_prefix)
    obj_3.set_ip_prefix_len('24')
    obj_2.set_subnet(obj_3)
    obj_1.add_ipam_subnets(obj_2)
    obj_0.add_network_ipam(my_ipam, obj_1)
    vn_id = vh.virtual_network_create(obj_0)
    my_vn_ids.append(vn_id)

print ("Creating a VPG")
my_vpg=vnc_api.VirtualPortGroup(name='my-vpg',parent_obj=my_fab)
my_vpg.set_virtual_port_group_type('access')
obj_1 = vnc_api.VpgInterfaceParametersType()
my_vpg.add_physical_interface(my_pi, obj_1)
my_vpg_id = vh.virtual_port_group_create(my_vpg)

if len(tag_list)!=len(my_vn_ids):
    print ("ERROR: There doesn't seem to be a correct mapping between VMIs and tags")

print ("Creating VMIs")
for my_vn_id in my_vn_ids:
    my_vn = vh.virtual_network_read(id=my_vn_id)
    vmi_name = 'vmi_' + str(my_vn_ids.index(my_vn_id))
    my_vmi=vnc_api.VirtualMachineInterface(name=vmi_name,parent_obj=my_proj)
    my_vmi.add_virtual_network(my_vn)
    kvps = vnc_api.KeyValuePairs()
    kvp = vnc_api.KeyValuePair()
    kvp.set_key("profile")
        lli = {}
    lli = {"local_link_information":[{"port_id":'',"switch_id":'',"switch_info":'',"fabric":''}]}
    lli['local_link_information'][0]['port_id']=str(phy_intf)
    lli['local_link_information'][0]['switch_id']=str(phy_intf)
    lli['local_link_information'][0]['switch_info']=str(switch)
    lli['local_link_information'][0]['fabric']=str(fabric_name)
    kvp.set_value(json.dumps(lli))

    kvps.add_key_value_pair(kvp)
    kvp = vnc_api.KeyValuePair()
    kvp.set_key("vpg")
    kvp.set_value("my-vpg")
    kvps.add_key_value_pair(kvp)

    kvp = vnc_api.KeyValuePair()
    kvp.set_key("vnic_type")
    kvp.set_value("baremetal")
    kvps.add_key_value_pair(kvp)

    kvp = vnc_api.KeyValuePair()
    kvp.set_key("vif_type")
    kvp.set_value("vrouter")
    kvps.add_key_value_pair(kvp)

    my_vmi.set_virtual_machine_interface_bindings(kvps)
    my_vmi.add_security_group(my_sg)
    obj_1 = vnc_api.VirtualMachineInterfacePropertiesType()
    obj_1.set_sub_interface_vlan_tag(tag_list[my_vn_ids.index(my_vn_id)])
    my_vmi.set_virtual_machine_interface_properties(obj_1)
    vmi_id=vh.virtual_machine_interface_create(my_vmi)
    my_vmi_ids.append(vmi_id)
print ("Updating VPG with the VMIs")
my_vpg = vh.virtual_port_group_read(id=my_vpg_id)
for my_vmi_id in my_vmi_ids:
    my_vmi=vh.virtual_machine_interface_read(id=my_vmi_id)
    my_vpg.add_virtual_machine_interface(my_vmi)
vh.virtual_port_group_update(my_vpg)