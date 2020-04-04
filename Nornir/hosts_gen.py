#Host file generator

print("---")
for i in range (1, 7):
    print("R" + str(i) + ":")
    print("    hostname: 192.168.78." + str(i))
    print("    groups:")
    print("        - cisco_group")
    if i == 2:
        print("    data:")
        print("        asn: 10")
    if i == 4:
        print("    data:")
        print("        asn: 20")
    if i == 6:
        print("    data:")
        print("        asn: 30")

