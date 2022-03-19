[TOC]

# File Tree

```bash
abigail@ubuntu:~/Desktop/TCPcongestion$ tree
.
├── multi #多对sender/reciver网络结构的实验
│   ├── bbr #采用bbr算法的mininet网络
│   │   ├── log #每对sender/reciver的iperf测试日志
│   │   │   ├── h1h2.txt
│   │   │   ├── h3h4.txt
│   │   │   ├── h5h6.txt
│   │   │   └── h7h8.txt
│   │   ├── multi_bbr.py #见上文
│   │   └── run.sh
│   └── reno #同上
│       ├── log
│       │   ├── h1h2.txt
│       │   ├── h3h4.txt
│       │   ├── h5h6.txt
│       │   └── h7h8.txt
│       ├── multi_reno.py
│       └── run.sh
└── single #一对sender/reciver网络结构的实验
    ├── bbr #采用bbr算法的mininet网络
    │   ├── haveall.py #self.addLink(switch1, switch2, bw=bottle, delay=delay, loss=loss, use_htb=True)
    │   ├── havebottle.py #self.addLink(switch1, switch2, bw=bottle, delay=nodelay, loss=noloss, use_htb=True)
    │   ├── havedelay.py #elf.addLink(switch1, switch2, bw=nobottle, delay=delay, loss=noloss, use_htb=True)
    │   ├── haveloss.py #self.addLink(switch1, switch2, bw=nobottle, delay=nodelay, loss=loss, use_htb=True)
    │   ├── havenon.py #self.addLink(switch1, switch2, bw=nobottle, delay=nodelay, loss=noloss, use_htb=True)
    │   ├── log #不同情况的网络的iperf测试日志
    │   │   ├── haveall.txt 
    │   │   ├── havebottle.txt 
    │   │   ├── havedelay.txt 
    │   │   ├── haveloss.txt 
    │   │   └── havenon.txt 
    │   └── run.sh
    └── reno #同上
        ├── haveall.py 
        ├── havebottle.py 
        ├── havedelay.py 
        ├── haveloss.py 
        ├── havenon.py 
        ├── log
        │   ├── haveall.txt
        │   ├── havebottle.txt
        │   ├── havedelay.txt
        │   ├── haveloss.txt
        │   └── havenon.txt
        └── run.sh
```





# Question

## 1.bbr 原理

> 除了TCP Reno之外，挑选一种TCP拥塞控制算法，并解释它是如何工作的。
>



bbr算法周期性地探测网络的容量，交替测量一段时间内的带宽极大值和时延极小值，将其乘积作为作为拥塞窗口大小（交替测量的原因是极大带宽和极小时延不可能同时得到，带宽极大时网络被填满造成排队，时延必然极大，时延极小时需要数据包不被排队直接转发，带宽必然极小），使得拥塞窗口始的值始终与网络的容量保持一致。



## 2.single reciver/sender 

> 构建一个只有一对发送器和接收器的网络。研究上述两个TCP版本的TCP吞吐量如何随链路带宽/链路延迟/丢失率而变化。

### 实验过程

构建一个拓扑结构如下的网络，设置s1-s2的参数, 并分别采用bbr和reno算法,对h1-h2链路进行iperf测试，将测试结果重定向输出到log文件夹下。

<img src="https://i.loli.net/2021/11/23/1ERYfuAhU4ibSq3.png" alt="image-20211123222959873" style="zoom:50%;" />

这里，s1-s2的参数取值如File Tree中设置，具体数值如下所示

```python
nobottle=500
bottle=100

nodelay='5ms'
delay='200ms'

noloss=0
loss=0.1
```

iperf 测试命令是：

```python
h1.cmd("iperf3 -s -p 5566 -i 1 &")#设置h1为发送方，其端口号为5566
h2.cmd("iperf3 -c 10.0.0.1 -p 5566 -t 15 -i 1 >log/haveall.txt")
```



### 实验结果

下表中的数据是不同情况下的**接收方**吞吐量（Bitrate或Throughout），单位为Mbits/sec

|                     | bbr  | reno |
| ------------------- | ---- | ---- |
| 理想情况            | 262  | 322  |
| 有瓶颈链路，bw=4    | 3.76 | 2.36 |
| 有时延，delay=200ms | 102  | 112  |
| 有丢包，loss=0.1    | 255  | 108  |
| 全都有              | 3.08 | 3.32 |

根据上表可以看出，在有丢包的情况下，bbr表现相较于reno有大幅度提升，这是因为bbr算法不将出现丢包或时延增加作为拥塞的信号，而是认为当网络上的数据包总量大于瓶颈链路带宽和时延的乘积时才出现了拥塞。

而reno算法将收到 ACK 这一信号作为拥塞窗口增长的依据，在早期低带宽、低时延的网络中能够很好的发挥作用，但是随着网络带宽和延时的增加，Reno 的缺点就渐渐体现出来了，发送端从发送报文到收到 ACK 经历一个 RTT，在高带宽延时（High Bandwidth-Delay Product，BDP）网络中，RTT 很大，导致拥塞窗口增长很慢，传输速度需要经过很长时间才能达到最大带宽，导致带宽利用率将低。

另外，观察两个算法的iperf测试日志中的Cwnd项变化趋势，可以看出两个算法拥塞窗口不同的调整策略

因此，reno适用于低延时、低带宽的网络；bbr适用于高带宽、高时延、有一定丢包率的长肥网络，可以有效降低传输时延，并保证较高的吞吐量。

## 3.multiple reciver/sender 

> 构建一个由多对发送方和接收方共享瓶颈链路的网络。研究这些发送者和接收者对如何共享瓶颈链路。

### 实验过程

构建一个拓扑结构如下的网络，设置s1-s2的参数为``bw=100, delay=5ms, loss=0.1, use_htb=True``, 并分别采用bbr和reno算法,对每条链路进行iperf测试，将测试结果重定向输出到log文件夹下。

<img src="https://i.loli.net/2021/11/23/U7dyB8HTZeE4lnu.png" alt="image-20211123222613812" style="zoom:50%;" />

这里，s1-s2的参数取值如下所示

```python
self.addLink(switch1, switch2, bw=10, delay=5ms, loss=0.1, use_htb=True)
```



iperf测试命令如下所示

```python
h1.cmd("iperf3 -s -p 5566 -i 1 &")#设置h1为发送方，其端口号为5566
h3.cmd("iperf3 -s -p 5566 -i 1 &")
h5.cmd("iperf3 -s -p 5566 -i 1 &")
h7.cmd("iperf3 -s -p 5566 -i 1 &")

h2.cmd("iperf3 -c 10.0.0.1 -p 5566 -t 15 -i 1 >log/h1h2.txt")
h4.cmd("iperf3 -c 10.0.0.3 -p 5566 -t 15 -i 1 >log/h3h4.txt")
h6.cmd("iperf3 -c 10.0.0.3 -p 5566 -t 15 -i 1 >log/h5h6.txt")
h8.cmd("iperf3 -c 10.0.0.3 -p 5566 -t 15 -i 1 >log/h7h8.txt")
```



### 实验结果

#### bbr

##### log/h7h8.txt

```bash
Connecting to host 10.0.0.3, port 5566
[  5] local 10.0.0.8 port 54074 connected to 10.0.0.3 port 5566
[ ID] Interval           Transfer     Bitrate         Retr  Cwnd
[  5]   0.00-1.00   sec  5.24 MBytes  43.9 Mbits/sec    0   1022 KBytes       
[  5]   1.00-2.00   sec  1.25 MBytes  10.5 Mbits/sec    0   2.13 MBytes       
[  5]   2.00-3.00   sec  7.50 MBytes  62.9 Mbits/sec    0   3.26 MBytes       
[  5]   3.00-4.00   sec  0.00 Bytes  0.00 bits/sec    0   4.40 MBytes       
[  5]   4.00-5.00   sec  1.25 MBytes  10.5 Mbits/sec    0   5.53 MBytes       
[  5]   5.00-6.00   sec  0.00 Bytes  0.00 bits/sec    3   6.35 MBytes       
[  5]   6.00-7.00   sec  0.00 Bytes  0.00 bits/sec    0   5.78 MBytes       
[  5]   7.00-8.00   sec  0.00 Bytes  0.00 bits/sec  213   4.62 MBytes       
[  5]   8.00-9.00   sec  0.00 Bytes  0.00 bits/sec  487   3.03 MBytes       
[  5]   9.00-10.00  sec  0.00 Bytes  0.00 bits/sec  951   3.23 MBytes       
[  5]  10.00-11.00  sec  1.25 MBytes  10.5 Mbits/sec    0   2.16 MBytes       
[  5]  11.00-12.00  sec  3.75 MBytes  31.4 Mbits/sec  747   3.14 MBytes       
[  5]  12.00-13.00  sec  2.50 MBytes  21.0 Mbits/sec    1   3.23 MBytes       
[  5]  13.00-14.00  sec  0.00 Bytes  0.00 bits/sec    0   3.23 MBytes       
[  5]  14.00-15.00  sec  0.00 Bytes  0.00 bits/sec  495   2.49 MBytes       
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Retr
[  5]   0.00-15.00  sec  22.7 MBytes  12.7 Mbits/sec  2897             sender
[  5]   0.00-17.10  sec  16.0 MBytes  7.84 Mbits/sec                  receiver

iperf Done.

```

##### log/h5h6.txt

```bash
Connecting to host 10.0.0.3, port 5566
[  5] local 10.0.0.6 port 60980 connected to 10.0.0.3 port 5566
[ ID] Interval           Transfer     Bitrate         Retr  Cwnd
[  5]   0.00-1.00   sec  3.06 MBytes  25.6 Mbits/sec    5    404 KBytes       
[  5]   1.00-2.00   sec  2.49 MBytes  20.9 Mbits/sec    0    311 KBytes       
[  5]   2.00-3.00   sec  0.00 Bytes  0.00 bits/sec    0    315 KBytes       
[  5]   3.00-4.00   sec  1.18 MBytes  9.91 Mbits/sec    2    167 KBytes       
[  5]   4.00-5.00   sec  1.18 MBytes  9.90 Mbits/sec    0    170 KBytes       
[  5]   5.00-6.00   sec  1.18 MBytes  9.91 Mbits/sec    1   91.9 KBytes       
[  5]   6.00-7.00   sec  1.18 MBytes  9.90 Mbits/sec    2   56.6 KBytes       
[  5]   7.00-8.00   sec  1.18 MBytes  9.91 Mbits/sec    4   33.9 KBytes       
[  5]   8.00-9.00   sec  1.18 MBytes  9.91 Mbits/sec    0   66.5 KBytes       
[  5]   9.00-10.00  sec  1.18 MBytes  9.90 Mbits/sec    0   87.7 KBytes       
[  5]  10.00-11.00  sec  1.24 MBytes  10.4 Mbits/sec    0    105 KBytes       
[  5]  11.00-12.00  sec  1.24 MBytes  10.4 Mbits/sec    0    119 KBytes       
[  5]  12.00-13.00  sec  1.18 MBytes  9.91 Mbits/sec    0    133 KBytes       
[  5]  13.00-14.00  sec  1.18 MBytes  9.91 Mbits/sec    0    144 KBytes       
[  5]  14.00-15.00  sec  1.24 MBytes  10.4 Mbits/sec    4   86.3 KBytes       
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Retr
[  5]   0.00-15.00  sec  19.9 MBytes  11.1 Mbits/sec   18             sender
[  5]   0.00-15.08  sec  16.8 MBytes  9.32 Mbits/sec                  receiver

iperf Done.

```

##### 总结

观察上面两个iperf测试日志，可以看出存在多条链路共享瓶颈链路时，bbr算法下

- 数据传输稳定性较差（bitrate波动剧烈，不同链路丢包率不同）
- 但是总的数据传输量相近（平均Bitrate和平均Transfer相近）。

#### reno

##### log/h7h8.txt

```bash
Connecting to host 10.0.0.3, port 5566
[  5] local 10.0.0.8 port 54142 connected to 10.0.0.3 port 5566
[ ID] Interval           Transfer     Bitrate         Retr  Cwnd
[  5]   0.00-1.00   sec  1.85 MBytes  15.5 Mbits/sec    2   69.3 KBytes       
[  5]   1.00-2.00   sec  1.30 MBytes  10.9 Mbits/sec    0    102 KBytes       
[  5]   2.00-3.00   sec  1.30 MBytes  10.9 Mbits/sec    0    102 KBytes       
[  5]   3.00-4.00   sec   891 KBytes  7.30 Mbits/sec    0   99.0 KBytes       
[  5]   4.00-5.00   sec  1.30 MBytes  10.9 Mbits/sec    2   99.0 KBytes       
[  5]   5.00-6.00   sec   891 KBytes  7.29 Mbits/sec    0    102 KBytes       
[  5]   6.00-7.00   sec  1.30 MBytes  10.9 Mbits/sec    0    102 KBytes       
[  5]   7.00-8.00   sec  1.37 MBytes  11.5 Mbits/sec    2   99.0 KBytes       
[  5]   8.00-9.00   sec   891 KBytes  7.30 Mbits/sec    0   99.0 KBytes       
[  5]   9.00-10.00  sec  1.30 MBytes  11.0 Mbits/sec    2   99.0 KBytes       
[  5]  10.00-11.00  sec   891 KBytes  7.29 Mbits/sec    0    105 KBytes       
[  5]  11.00-12.00  sec   891 KBytes  7.30 Mbits/sec    2    102 KBytes       
[  5]  12.00-13.00  sec  1.30 MBytes  11.0 Mbits/sec    0    102 KBytes       
[  5]  13.00-14.00  sec  1.30 MBytes  10.9 Mbits/sec    0    102 KBytes       
[  5]  14.00-15.00  sec   891 KBytes  7.29 Mbits/sec    0    102 KBytes       
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Retr
[  5]   0.00-15.00  sec  17.6 MBytes  9.83 Mbits/sec   10             sender
[  5]   0.00-15.09  sec  16.8 MBytes  9.33 Mbits/sec                  receiver

iperf Done.


```

##### log/h5h6.txt

```bash
Connecting to host 10.0.0.3, port 5566
[  5] local 10.0.0.6 port 32818 connected to 10.0.0.3 port 5566
[ ID] Interval           Transfer     Bitrate         Retr  Cwnd
[  5]   0.00-1.00   sec  1.91 MBytes  16.0 Mbits/sec    2   99.0 KBytes       
[  5]   1.00-2.00   sec  1.30 MBytes  11.0 Mbits/sec    0    102 KBytes       
[  5]   2.00-3.00   sec   891 KBytes  7.29 Mbits/sec    0    105 KBytes       
[  5]   3.00-4.00   sec  1.30 MBytes  10.9 Mbits/sec    0    102 KBytes       
[  5]   4.00-5.00   sec  1.30 MBytes  10.9 Mbits/sec    0    102 KBytes       
[  5]   5.00-6.00   sec   891 KBytes  7.30 Mbits/sec    4    102 KBytes       
[  5]   6.00-7.00   sec  1.30 MBytes  10.9 Mbits/sec    0    105 KBytes       
[  5]   7.00-8.00   sec  1.30 MBytes  11.0 Mbits/sec    2    102 KBytes       
[  5]   8.00-9.00   sec   891 KBytes  7.30 Mbits/sec    0   99.0 KBytes       
[  5]   9.00-10.00  sec  1.30 MBytes  10.9 Mbits/sec    0    102 KBytes       
[  5]  10.00-11.00  sec   891 KBytes  7.30 Mbits/sec    0   96.2 KBytes       
[  5]  11.00-12.00  sec   891 KBytes  7.30 Mbits/sec    0   99.0 KBytes       
[  5]  12.00-13.00  sec  1.30 MBytes  11.0 Mbits/sec    4   99.0 KBytes       
[  5]  13.00-14.00  sec  1.30 MBytes  10.9 Mbits/sec    0   96.2 KBytes       
[  5]  14.00-15.00  sec   891 KBytes  7.30 Mbits/sec    0    102 KBytes       
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Retr
[  5]   0.00-15.00  sec  17.6 MBytes  9.83 Mbits/sec   12             sender
[  5]   0.00-15.09  sec  16.8 MBytes  9.34 Mbits/sec                  receiver

iperf Done.

```

##### 总结

观察上面两个iperf测试日志，可以看出存在多条链路共享瓶颈链路时，reno算法下

- 数据传输稳定性较好（bitrate波动不大，丢包率不大）
- 总的数据传输量相近（平均Bitrate和平均Transfer相近）
- 可以看出，两条链路的吞吐量波动情况如下图所示：

<img src="https://i.loli.net/2021/11/23/GbEkoYMp9QqVxJl.jpg" alt="IMG_0BE7D6D84996-1" style="zoom:50%;" />

