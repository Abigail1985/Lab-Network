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
bottle=10

nodelay='5ms'
delay='200ms'

noloss=0
loss=0.1

class MultiSenderReciverTopo( Topo ):
    def build( self ):
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')

        host1 = self.addHost('h1', cpu=.25)
        host2 = self.addHost('h2', cpu=.25)
        self.addLink(host1, switch1, bw=500, delay='5ms', loss=0, use_htb=True)
        self.addLink(host2, switch2, bw=500, delay='5ms', loss=0, use_htb=True)

        host3 = self.addHost('h3', cpu=.25)
        host4 = self.addHost('h4', cpu=.25)
        self.addLink(host3, switch1, bw=500, delay='5ms', loss=0, use_htb=True)
        self.addLink(host4, switch2, bw=500, delay='5ms', loss=0, use_htb=True)

        host5 = self.addHost('h5', cpu=.25)
        host6 = self.addHost('h6', cpu=.25)
        self.addLink(host5, switch1, bw=500, delay='5ms', loss=0, use_htb=True)
        self.addLink(host6, switch2, bw=500, delay='5ms', loss=0, use_htb=True)

        host7 = self.addHost('h7', cpu=.25)
        host8 = self.addHost('h8', cpu=.25)
        self.addLink(host7, switch1, bw=500, delay='5ms', loss=0, use_htb=True)
        self.addLink(host8, switch2, bw=500, delay='5ms', loss=0, use_htb=True)

        self.addLink(switch1, switch2, bw=bottle, delay=nodelay, loss=loss, use_htb=True)





def Test(tcp):
    "Create network and run simple performance test"
    topo = MultiSenderReciverTopo()
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

    # h1,h2,h3,h4= net.getNodeByName('h1','h2','h3','h4')

    h1,h2,h3,h4,h5,h6,h7,h8= net.getNodeByName('h1','h2','h3','h4','h5','h6','h7','h8')
    h1.cmd("iperf3 -s -p 5566 -i 1 &")#设置h1为发送方，其端口号为5566
    h3.cmd("iperf3 -s -p 5566 -i 1 &")#设置h1为发送方，其端口号为5566
    h5.cmd("iperf3 -s -p 5566 -i 1 &")#设置h1为发送方，其端口号为5566
    h7.cmd("iperf3 -s -p 5566 -i 1 &")#设置h1为发送方，其端口号为5566

    h2.cmd("iperf3 -c 10.0.0.1 -p 5566 -t 15 -i 1 >log/h1h2.txt")
    h4.cmd("iperf3 -c 10.0.0.3 -p 5566 -t 15 -i 1 >log/h3h4.txt")
    h6.cmd("iperf3 -c 10.0.0.3 -p 5566 -t 15 -i 1 >log/h5h6.txt")
    h8.cmd("iperf3 -c 10.0.0.3 -p 5566 -t 15 -i 1 >log/h7h8.txt")

    
    # CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    # pick a congestion control algorithm, for example, 'reno', 'cubic', 'bbr', 'vegas', 'hybla', etc.
    tcp = 'bbr'
    Test(tcp)
