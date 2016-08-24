# Scale Test
#
# This program is intended to describe a scaling test procedure for OpenDaylight NetVirt.
# It could be used for other network virtualization implementations as well.
#
# As is, it's mostly a simulation, but the various print statements could be replaced by
# actual calls to do the work.
#
# @author: Andre Fredette, Red Hat Inc.
#

NUM_SERVERS = 20
PORTS_PER_SERVER = 2
PORTS_PER_NETWORK = 2
NETWORKS_PER_ROUTER = 2
CONCURRENT_NETWORKS = 2
CONCURRENT_ROUTERS = 2
FLOATING_IP_PER_NUM_PORTS = 2


class Network:
    next_network_id = 0      #
    next_network_index = 0   # Index used to loop through concurrent networks.

    def __init__(self, max_ports):
        self.id = Network.next_network_id
        self.num_ports = 0
        self.router_port_added = False
        self.max_ports = max_ports
        Network.next_network_id += 1

    def re_init(self):
        Network.__init__(self, self.max_ports)

    def add_port(self, port_id):
        if self.max_ports > 0:
            if self.num_ports < self.max_ports:
                print "Adding port " + str(port_id) + " to Network " + str(self.id)
                self.num_ports += 1
            else:
                self.re_init()
                print "Creating Network " + str(self.id)
                print "Adding port " + str(port_id) + " to Network " + str(self.id)
                self.num_ports += 1

    def add_router_port(self):
        self.router_port_added = True


class Router:
    next_router_id = 0
    next_router_index = 0

    def __init__(self, max_ports):
        self.id = Router.next_router_id
        self.num_ports = 0
        self.max_ports = max_ports
        Router.next_router_id += 1

    def re_init(self):
        Router.__init__(self, self.max_ports)

    def add_port(self, network):
        if self.max_ports > 0 and network.router_port_added == False:
            if self.num_ports < self.max_ports:
                print "Adding Network " + str(network.id) + " to Router " + str(self.id)
                self.num_ports += 1
            else:
                self.re_init()
                print "Creating Router " + str(self.id)
                print "Adding Network " + str(network.id) + " to Router " + str(self.id)
                self.num_ports += 1
            network.add_router_port()


def run_scale_test(num_servers, ports_per_server, ports_per_network, networks_per_router,
                   concurrent_networks, concurrent_routers, floating_ip_per_num_ports):

    print "\nScale Test\n"

    # Init Networks
    networks = []
    for network in range(0, concurrent_networks):
        networks.append(Network(ports_per_network))
        print "Creating Network " + str(networks[network].id)

    next_network_index = 0

    print ""

    # Init Routers
    routers = []
    for router in range(0, concurrent_routers):
        routers.append(Router(networks_per_router))
        print "Creating Router " + str(routers[router].id)

    next_router_index = 0

    print ""

    # Init External Network
    if floating_ip_per_num_ports > 0:
        print "Creating External Network\n"

    next_port_id = 0

    for server in range(0, num_servers):
        for port in range (0, ports_per_server):
            print "Creating port " + str(next_port_id) + " on Server " + str(server)

            # Add port to network, if necessary
            if concurrent_networks > 0:
                networks[next_network_index].add_port(next_port_id)

                # Add network to router, if necessary
                if concurrent_routers > 0:
                    routers[next_router_index].add_port(networks[next_network_index])
                    next_router_index = (next_router_index +1) % concurrent_routers;

                    # Create floating IP for port if necessary.
                    if floating_ip_per_num_ports > 0 and next_port_id % floating_ip_per_num_ports == 0:
                        print "Creating a Floating IP for Port " + str(next_port_id)

                next_network_index = (next_network_index + 1) % concurrent_networks;

            next_port_id += 1
            print ""


run_scale_test(NUM_SERVERS, PORTS_PER_SERVER, PORTS_PER_NETWORK, NETWORKS_PER_ROUTER,
               CONCURRENT_NETWORKS, CONCURRENT_ROUTERS, FLOATING_IP_PER_NUM_PORTS)