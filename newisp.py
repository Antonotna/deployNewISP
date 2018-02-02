import sys
from netaddr import *

def main():
	try:
		ispName = input('Description ISP: ')
		ispBGPName = input('BGP ISP Name: ')
		regAS = input('Region BGP AS: ')
		ispAS = input('ISP BGP AS: ')
		ispID = input('ISP ID: ')
		ispBW = input('ISP bandwidth: ')
		ispIafce = input('ISP Interface: ')
		ispNetLM = IPNetwork(input('CE-PE Network (with net prefix): '))
		ispNetAll = IPNetwork(input('Whole ISP Network (with net prefix): '))
	except KeyboardInterrupt:
		sys.exit('\nEXit\n')
	except:
		sys.exit('\n!Wrong Parameters!\n')

	branchIP = str(IPAddress(ispNetLM.first+1))
	branchGW = str(IPAddress(ispNetLM.last-1))
	branchMask = str(ispNetLM.netmask)
	
	#Template
	print('\n-----------Config--------------\n')

	#interface
	print('!\n\
interface %s\n\
 description %s L3 %s $notm\n\
 bandwidth qos-reference %s\n\
 bandwidth %s\n\
 ip address %s %s\n\
 ip flow ingress\n\
 ip flow egress\n\
 load-interval 30\n\
 duplex auto\n\
 speed auto\n\
 no cdp enable\n\
 service-policy output shape-policy-out\n\
			' % ( (ispIafce, ispName, ispID) + (ispBW,)*2 + (branchIP, branchMask) ) )

	#Route Map
	print('!\n\
route-map bgp-%s-in permit 10\n\
 set local-preference 40\n\
route-map bgp-%s-out permit 10\n\
 set as-path prepend 65072 65072 65072 65072\n\
			' % ((ispBGPName.lower(),)*2) )

	#BGP
	print('!\n\
router bgp %s\n\
 neighbor %s peer-group\n\
 neighbor %s remote-as %s\n\
 neighbor %s version 4\n\
 neighbor %s send-community both\n\
 neighbor %s soft-reconfiguration inbound\n\
 neighbor %s route-map bgp-%s-in in\n\
 neighbor %s route-map bgp-%s-out out\n\
 neighbor %s filter-list 1 out\n\
 neighbor %s peer-group %s\n\
 neighbor %s update-source %s\n\
			' % ((regAS,) + (ispBGPName,)*2 + (ispAS,) + (ispBGPName,)*3 + (ispBGPName,ispBGPName.lower())*2 + (ispBGPName,) + (branchGW,) + (ispBGPName,) + (branchGW,) + (ispIafce,)))

	#Routing
	print('!\n\
ip route %s %s %s %s name %s-IPVPN\n\
			' % (str(ispNetAll.network),str(ispNetAll.netmask),ispIafce,branchGW,ispBGPName))

	#Local PBR
	print('!\n\
access-list 3 permit %s\n\
route-map local-pbr permit 20\n\
 match ip address 3\n\
 set ip next-hop %s\n\
			' % (branchIP,branchGW))



if(__name__ == '__main__'):
	main()