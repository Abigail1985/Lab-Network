from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER 
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
import _thread
import time

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        print("hello")
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        _thread.start_new_thread(self.flow_table_initial,(self,datapath,parser,ofproto))
        

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    #这个控制器只使用一条线路：h1-s1-s3-s2-h1,从而避免了arp风暴    
    def flow_table_initial(self, datapath,parser,ofproto):
        if datapath.id==1:
            actions = [parser.OFPActionOutput ( 1 )] 
            match = parser.OFPMatch ( in_port=3 ) 
            self.add_flow( datapath, 10, match, actions )

            actions = [parser.OFPActionOutput ( 1 )] 
            match = parser.OFPMatch ( in_port=2 ) 
            self.add_flow( datapath, 10, match, actions )        

            actions = [parser.OFPActionOutput ( 2 )] 
            match = parser.OFPMatch ( in_port=1 ) 
            self.add_flow( datapath, 10, match, actions )

        if datapath.id==2:
            actions = [parser.OFPActionOutput ( 1 )] 
            match = parser.OFPMatch ( in_port=3 ) 
            self.add_flow( datapath, 10, match, actions )

            actions = [parser.OFPActionOutput ( 1 )] 
            match = parser.OFPMatch ( in_port=2 ) 
            self.add_flow( datapath, 10, match, actions )        

            actions = [parser.OFPActionOutput ( 2 )] 
            match = parser.OFPMatch ( in_port=1 ) 
            self.add_flow( datapath, 10, match, actions )

        if datapath.id==3:
            actions = [parser.OFPActionOutput ( 1 )] 
            match = parser.OFPMatch ( in_port=2 ) 
            self.add_flow( datapath, 10, match, actions )

            actions = [parser.OFPActionOutput ( 2 )] 
            match = parser.OFPMatch ( in_port=1 ) 
            self.add_flow( datapath, 10, match, actions )

        if datapath.id==4:
            actions = [parser.OFPActionOutput ( 1 )] 
            match = parser.OFPMatch ( in_port=2 ) 
            self.add_flow( datapath, 10, match, actions )

            actions = [parser.OFPActionOutput ( 2 )] 
            match = parser.OFPMatch ( in_port=1 ) 
            self.add_flow( datapath, 10, match, actions )