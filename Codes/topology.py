from mininet.cli import CLI
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.topo import SingleSwitchTopo

#Mininet topology with 3 hosts and 1 swtich
def main():
    setLogLevel('info')                 # Set log level to into to see more output
    sst = SingleSwitchTopo(k=3)         # Create topology with 3 hosts
    net = Mininet(sst)                  # Start network from topology
    net.start()                         # Start network
    CLI(net)                            # Start CLI to interact with network
    net.stop()                          # Stop network
  
if __name__ == '__main__':
    main()
