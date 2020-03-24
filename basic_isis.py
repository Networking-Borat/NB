from netmiko import ConnectHandler


routers = '''
R1
R2
R3
R4
R5
R6
R7
R8
R9
R10
R11
R12
R13
R14
'''.strip().splitlines()

device_type = 'cisco_ios'
username = 'kamil'
password = 'cisco'
verbose = True

for router in routers:
    print(" Connecting to Router: " + router)
    net_connect = ConnectHandler (ip=router, device_type=device_type, username=username, password=password)
    prompter = net_connect.find_prompt()
    if '>' in prompter:
            net_connect.enable()

    output = net_connect.send_command('show run | sec isis')
    
    if len(router[1:]) == 1:
        isis_commands = ['router isis', 'net 49.0001.0000.0000.000' + router[1:] + '.00', 'is-type level-1', 'exit', 'int range g0/1-2', 'ip router isis']
    elif len(router[1:]) == 2:
        isis_commands = ['router isis', 'net 49.0001.0000.0000.00' + router[1:] + '.00', 'is-type level-1', 'exit', 'int range g0/1-2', 'ip router isis']
    elif len(router[1:]) == 3:
        isis_commands = ['router isis', 'net 49.0001.0000.0000.0' + router[1:] + '.00', 'is-type level-1', 'exit', 'int range g0/1-2', 'ip router isis']
    else:
        print("Not suitable hostname, please verify hosts file & router host names")
    if not 'router isis' in output:
         print('ISIS is not enabled on device: ' + router)
         answer = input('Would you like to enable default ISIS settings on: ' + router + ' <y/n> ')
         if answer == 'y':
             output = net_connect.send_config_set(isis_commands)
             print(output)
             print('ISIS is now configued!')
         else:
             print('No ISIS configurations have been made!')

    else:
        print("ISIS is already configured on device: " + router)

