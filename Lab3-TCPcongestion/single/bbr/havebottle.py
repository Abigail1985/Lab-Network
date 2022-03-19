#!/usr/bin/python

"""
Simple example of setting network and CPU parameters  
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import quietRun, dumpNodeConnections
from mininet.log import setLogLevel, info
from mininet.cli import CLI

from sys import argv
import time

nobottle=500
bottle=4

nodelay='5ms'
delay='200ms'

noloss=0
loss=0.1

class SingleSwitchTopo( Topo ):
    def build( self ):
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        host1 = self.addHost('h1', cpu=.25)
        host2 = self.addHost('h2', cpu=.25)
        self.addLink(host1, switch1, bw=500, delay='5ms', loss=0, use_htb=True)
        self.addLink(host2, switch2, bw=500, delay='5ms', loss=0, use_htb=True)
        self.addLink(switch1, switch2, bw=bottle, delay=nodelay, loss=noloss, use_htb=True)

def Test(tcp):
    "Create network and run simple performance test"
    topo = SingleSwitchTopo()
    net = Mininet( topo=topo,
                   host=CPULimitedHost, link=TCLink,
                   autoStaticArp=False )
    net.start()

    # 验证连接
    info( "\nDumping host connections\n" )
    dumpNodeConnections(net.hosts)

    # 设定TCP拥塞协议
    output = quietRun( 'sysctl -w net.ipv4.tcp_congestion_control=' + tcp )
    assert tcp in output


    h1, h2 = net.getNodeByName('h1', 'h2')
    h1.cmd("iperf3 -s -p 5566 -i 1 &")#设置h1为发送方，其端口号为5566
    h2.cmd("iperf3 -c 10.0.0.1 -p 5566 -t 15 -i 1 >log/havebottle.txt")

    # CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    # pick a congestion control algorithm, for example, 'reno', 'cubic', 'bbr', 'vegas', 'hybla', etc.
    tcp = 'bbr'
    Test(tcp)
