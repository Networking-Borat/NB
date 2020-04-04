from nornir import InitNornir
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks.networking import netmiko_send_config, netmiko_send_command
from nornir.core.filter import F

#Specify the config file
nr = InitNornir(config_file="config.yaml", dry_run=True)

#Is-IS Internal Routers Configuration
def isis_internal(task):

    #Extracting the Router's "ID" from it's IP address
    pos = str(f"{task.host.hostname}").rfind('.')
    id = str(f"{task.host.hostname}")[pos + 1:]
    loopback_ip = "1.1.1." + str(id)

    # Selecting the Correct Length of IS-IS net Command According to the Router's ID Length (Level-1)
    if len(id) == 1:
        isis_commands = ["router isis", "net 49.0001.0000.0000.000" + str(id) + ".00", "is-type level-1"]
    elif len(id) == 2:
        isis_commands = ["router isis", "net 49.0001.0000.0000.00" + str(id) + ".00", "is-type level-1"]
    elif len(id) == 3:
        isis_commands = ["router isis", "net 49.0001.0000.0000.0" + str(id) + ".00", "is-type level-1"]
    deploy_isis = task.run(netmiko_send_config, config_commands=isis_commands)

    # Router's Loopback Configuration
    loopback_commands = ["interface loopback0", "ip address " + loopback_ip + " 255.255.255.255", "ip router isis"]
    deploy_loopback = task.run(netmiko_send_config, config_commands=loopback_commands)

    # Configuration of the Link to the Edge
    internal_to_edge_commands = ["int g0/0", "ip address 10.0.0.1 255.255.255.252", "ip router isis", "no shut"]
    deploy_int_to_edge = task.run(netmiko_send_config, config_commands=internal_to_edge_commands)

    # Configuration of the Loopback Interfaces (Simulated networks)
    for loopid in range(1, 5):
        loopid = str(loopid)
        internal_loopbacks = [" int lo" + loopid, "ip address 10.0." + loopid + ".1 255.255.255.0", "ip router isis"]
        deploy_int_looopbacks = task.run(netmiko_send_config, config_commands=internal_loopbacks)



def isis_edge(task):

    # Extracting the Router's "ID" from it's IP address
    pos = str(f"{task.host.hostname}").rfind('.')
    id = str(f"{task.host.hostname}")[pos + 1:]
    loopback_ip = "1.1.1." + str(id)

    # Information About the ISP Connection
    isis_edge_int = "200.0.0.1 255.255.255.252"
    isp_int = "200.0.0.2"
    isp_asn = "100"

    # Selecting the Correct Length of IS-IS net Command According to the Router's ID Length (Level-1-2)
    if len(id) == 1:
        isis_commands = ["router isis", "net 49.0001.0000.0000.000" + str(id) + ".00", "is-type level-1-2",
                         "default-information originate route-map SET-LEVEL1"]
    elif len(id) == 2:
        isis_commands = ["router isis", "net 49.0001.0000.0000.00" + str(id) + ".00", "is-type level-1-2",
                         "default-information originate route-map SET-LEVEL1"]
    elif len(id) == 3:
        isis_commands = ["router isis", "net 49.0001.0000.0000.0" + str(id) + ".00", "is-type level-1-2",
                         "default-information originate route-map SET-LEVEL1"]

    # Router's Loopback Configuration
    loopback_commands = ["interface loopback0", "ip address " + loopback_ip + " 255.255.255.255", "ip router isis"]
    deploy_loopback = task.run(netmiko_send_config, config_commands=loopback_commands)

    # Configuration of the Link to the ISP + Default Route + Route Map
    edge_commands = ["int g0/1", "ip address " + isis_edge_int, "no shut", "exit", "ip route 0.0.0.0 0.0.0.0 g0/1",
                     "route-map SET-LEVEL1 permit 10",
                     "set level level-1", "exit", "router bgp " + str(task.host["asn"]),
                     "neighbor " + isp_int + " remote-as " + isp_asn]

    # Configuration of internal Links
    edge_internal_commands = ["int g0/0", "ip address 10.0.0.2 255.255.255.252", "ip router isis", "no shut"]

    # Deployment
    deploy_edge_isis = task.run(netmiko_send_config, config_commands=isis_commands)
    deploy_edge = task.run(netmiko_send_config, config_commands=edge_commands)
    deploy_internal_edge = task.run(netmiko_send_config, config_commands =edge_internal_commands)


#OSPF Internal Configuration
def ospf_internal(task):

    # Extracting the Router's "ID" from it's IP address
    pos = str(f"{task.host.hostname}").rfind('.')
    id = str(f"{task.host.hostname}")[pos + 1:]
    loopback_ip = "1.1.1." + str(id)

    # Router's Loopback Configuration
    loopback_commands = ["interface loopback0", "ip address " + loopback_ip + " 255.255.255.255", "ip ospf 1 area 0"]
    deploy_loopback = task.run(netmiko_send_config, config_commands=loopback_commands)

    # Configuration of the link to the edge
    internal_to_edge_commands = ["int g0/0", "ip address 20.0.0.1 255.255.255.252", "ip ospf 1 area 0", "no shut"]
    deploy_int_to_edge = task.run(netmiko_send_config, config_commands=internal_to_edge_commands)

    # Configuration of the OSPF
    ospf_commands = ["router ospf 1", "router-id " + loopback_ip]
    deploy_ospf = task.run(netmiko_send_config, config_commands=ospf_commands)

    # Configuration of the Loopback Interfaces (Simulated networks)
    for loopid in range(1, 5):
        loopid = str(loopid)
        internal_loopbacks = [" int lo" + loopid, "ip address 20.0." + loopid + ".1 255.255.255.0", "ip ospf 1 area 0"]
        deploy_int_looopbacks = task.run(netmiko_send_config, config_commands=internal_loopbacks)



#OSPF Edge Configuration
def ospf_edge(task):

    # Extracting the Router's "ID" from it's IP address
    pos = str(f"{task.host.hostname}").rfind('.')
    id = str(f"{task.host.hostname}")[pos + 1:]
    loopback_ip = "1.1.1." + str(id)

    # Information About the ISP Connection
    ospf_edge_int = "200.0.2.1 255.255.255.252"
    isp_int = "200.0.2.2"
    isp_asn = "100"

    # Router's Loopback Configuration
    loopback_commands = ["interface loopback0", "ip address " + loopback_ip + " 255.255.255.255", "ip ospf 1 area 0"]
    deploy_loopback = task.run(netmiko_send_config, config_commands=loopback_commands)

    # Configuration of the Link to the ISP + Default Route
    edge_commands = ["int g0/1", "ip address " + ospf_edge_int, "no shut", "exit", "ip route 0.0.0.0 0.0.0.0 g0/1",
                     "router bgp " + str(task.host["asn"]),
                     "neighbor " + isp_int + " remote-as " + isp_asn]

    # Configuration of internal Links
    edge_internal_commands = ["int g0/0", "ip address 20.0.0.2 255.255.255.252", "ip ospf 1 area 0", "no shut"]

    # Configuration of the OSPF
    ospf_commands = ["router ospf 1", "default-information originate", "router-id " + loopback_ip]

    # Deployment
    deploy_internal_edge = task.run(netmiko_send_config, config_commands=edge_internal_commands)
    deploy_edge = task.run(netmiko_send_config, config_commands=edge_commands)
    deploy_ospf = task.run(netmiko_send_config, config_commands=edge_commands)



#EIGRP Internal Configuration
def eigrp_internal(task):

    # Extracting the Router's "ID" from it's IP address
    pos = str(f"{task.host.hostname}").rfind('.')
    id = str(f"{task.host.hostname}")[pos + 1:]
    loopback_ip = "1.1.1." + str(id)

    # Router's Loopback Configuration
    loopback_commands = ["interface loopback0", "ip address " + loopback_ip + " 255.255.255.255"]
    deploy_loopback = task.run(netmiko_send_config, config_commands=loopback_commands)

    # Configuration of the link to the edge
    internal_to_edge_commands = ["int g0/0", "ip address 10.0.0.1 255.255.255.252", "ip router isis", "no shut"]
    deploy_int_to_edge = task.run(netmiko_send_config, config_commands=internal_to_edge_commands)

    # Configuration of the EIGRP
    eigrp_commands = ["router eigrp 10", "no auto", "network " + loopback_ip + " 0.0.0.0", "network 30.0.0.0 0.0.0.3", "network 30.0.0.0 0.0.3.255"]
    deploy_eigrp = task.run(netmiko_send_config, config_commands=eigrp_commands)

    # Configuration of the Loopback Interfaces (Simulated networks)
    for loopid in range(1, 5):
        loopid = str(loopid)
        internal_loopbacks = [" int lo" + loopid, "ip address 30.0." + loopid + ".1 255.255.255.0"]
        deploy_int_looopbacks = task.run(netmiko_send_config, config_commands=internal_loopbacks)



#EIGRP Edge Configuration
def eigrp_edge(task):

    # Extracting the Router's "ID" from it's IP address
    pos = str(f"{task.host.hostname}").rfind('.')
    id = str(f"{task.host.hostname}")[pos + 1:]
    loopback_ip = "1.1.1." + str(id)

    # Information About the ISP Connection
    eigrp_edge_int = "200.0.4.1 255.255.255.252"
    isp_int = "200.0.4.2"
    isp_asn = "100"

    # Router's Loopback Configuration
    loopback_commands = ["interface loopback0", "ip address " + loopback_ip + " 255.255.255.255"]
    deploy_loopback = task.run(netmiko_send_config, config_commands=loopback_commands)

    # Configuration of the Link to the ISP + Default Route
    edge_commands = ["int g0/1", "ip address " + eigrp_edge_int, "no shut", "exit", "ip route 0.0.0.0 0.0.0.0 g0/1",
                     "router bgp " + str(task.host["asn"]),
                     "neighbor " + isp_int + " remote-as " + isp_asn]

    # Configuration of the Internal Links
    edge_internal_commands = ["int g0/0", "ip address 30.0.0.2 255.255.255.252", "no shut"]

    # Configuration of the EIGRP
    eigrp_commands = ["router eigrp 10", "no auto", "redistribute static", "network " + loopback_ip + " 0.0.0.0",
                      "network 30.0.0.0 0.0.0.3"]

    # Deployment
    deploy_edge = task.run(netmiko_send_config, config_commands=edge_commands)
    deploy_edge_internal = task.run(netmiko_send_config, config_commands=edge_internal_commands)
    deploy_eigrp = task.run(netmiko_send_config, config_commands=eigrp_commands)


# General Configuration for All Routers
def general_config(task):

    task.run(task=netmiko_send_config, config_file= "general_config")
    task.run(task=netmiko_send_command, command_string = "show run")



# Internal IS-IS
isis_internal_routers = nr.filter(type="internal_isis")
results = isis_internal_routers.run(task = isis_internal)

print_title("DEPLOYING CONFIGURATIONS")
print_result(results)



# Edge IS-IS
isis_edge_routers = nr.filter(type="edge_isis")
results = isis_edge_routers.run(task = isis_edge)

print_title("DEPLOYING CONFIGURATIONS")
print_result(results)



# Internal OSPF
ospf_internal_routers = nr.filter(type="internal_ospf")
results = ospf_internal_routers.run(task = ospf_internal)

print_title("DEPLOYING CONFIGURATIONS")
print_result(results)



# Edge OSPF
ospf_edge_routers = nr.filter(type="edge_ospf")
results = ospf_edge_routers.run(task = ospf_edge)

print_title("DEPLOYING CONFIGURATIONS")
print_result(results)



# Internal EIGRP
eigrp_internal_routers = nr.filter(type="internal_eigrp")
results = eigrp_internal_routers.run(task = eigrp_internal)

print_title("DEPLOYING CONFIGURATIONS")
print_result(results)



# Edge EIGRP
eigrp_edge_routers = nr.filter(type="edge_eigrp")
results = eigrp_edge_routers.run(task = eigrp_edge)

print_title("DEPLOYING CONFIGURATIONS")
print_result(results)



# General Configuration
general_configuration = nr.filter(F(groups__contains="all"))
results = general_configuration.run(task = general_config)

print_title("DEPLOYING CONFIGURATIONS")
print_result(results)
