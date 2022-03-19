#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from sys import argv
import time
# It would be nice if we didn't have to do this:
# pylint: disable=arguments-differ

class SingleSwitchTopo( Topo ):
    "Single switch connected to n hosts."
    def build( self, n=6, lossy=False ):
        switch = self.addSwitch('s1')
        for h in range(n):
            # Each host gets 50%/n of system CPU
            host = self.addHost('h%s' % (h + 1),
                                cpu=.5 / n)
            if lossy:
                # 10 Mbps, 5ms delay, 10% packet loss
                self.addLink(host, switch,
                             bw=10, delay='5ms', loss=10, use_htb=True)
            else:
                # 10 Mbps, 5ms delay, no packet loss
                self.addLink(host, switch,
                             bw=10, delay='5ms', loss=0, use_htb=True)

def perfTest( lossy=False ):
    "Create network and run simple performance test"
    topo = SingleSwitchTopo()
    net = Mininet( topo=topo,
                   host=CPULimitedHost, link=TCLink,
                   autoStaticArp=True )
    net.start()
    info( "Dumping host connections\n" )
    dumpNodeConnections(net.hosts)

 
    h1,c1,c2,c3,c4,c5=net.getNodeByName('h1','h2','h3','h4','h5','h6')
    
    h1.cmd("cd server_computer")

    c1.cmd("cd client_computer/c1")
    c2.cmd("cd client_computer/c2")
    c3.cmd("cd client_computer/c3")
    c4.cmd("cd client_computer/c4")
    c5.cmd("cd client_computer/c5")


    info(h1.cmd("./serverapp &"))
    
    time.sleep(3)
    info(c1.cmd ("./clientapp"))
    info(c2.cmd ("./clientapp" ))
    info(c3.cmd ("./clientapp" ))
    info(c4.cmd ("./clientapp" ))
    info(c5.cmd ("./clientapp" ))


    time.sleep(3)
    net.stop()

    
if __name__ == '__main__':
    setLogLevel( 'info' )

    perfTest()
    print('Mission complete, bye!')
