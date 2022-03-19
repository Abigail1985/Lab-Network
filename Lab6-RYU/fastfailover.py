from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER,DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
import _thread


class FastFailOver(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(FastFailOver, self).__init__(*args, **kwargs)


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        print("hello!!")
        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser

        _thread.start_new_thread(self.flow_table_initial,(datapath,parser))
        print("Successfully add group/flow table for: ",datapath.id)



    def send_group_mod(self,datapath):
        parser =datapath.ofproto_parser
        ofp=datapath.ofproto

        port = 3
        actions_1 = [parser.OFPActionOutput(port)]
        port = 2
        actions_2 = [parser.OFPActionOutput(port)]

        buckets = [
                    parser.OFPBucket (watch_port=3, actions=actions_1 ),
                    parser.OFPBucket (watch_port=2, actions=actions_2 )]


        group_id = 0
        req = parser.OFPGroupMod(datapath, ofp.OFPFC_ADD,ofp.OFPGT_FF, group_id, buckets)
        datapath.send_msg(req)

        actions = [parser.OFPActionGroup(group_id=group_id)]
        match = parser.OFPMatch(in_port=1)
        self.add_flow(datapath, 10, match, actions)    


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

    def flow_table_initial(self,datapath,parser):
        if datapath.id==1:       

            actions = [parser.OFPActionOutput ( 1 )] 
            match = parser.OFPMatch ( in_port=3 ) 
            self.add_flow( datapath, 10, match, actions )

            actions = [parser.OFPActionOutput ( 1 )] 
            match = parser.OFPMatch ( in_port=2 ) 
            self.add_flow( datapath, 10, match, actions )   

            self.send_group_mod(datapath)           

        if datapath.id==2: 
            actions = [parser.OFPActionOutput ( 1 )] 
            match = parser.OFPMatch ( in_port=2 ) 
            self.add_flow( datapath, 10, match, actions )        

            actions = [parser.OFPActionOutput ( 1 )] 
            match = parser.OFPMatch ( in_port=3 ) 
            self.add_flow( datapath, 10, match, actions )

            self.send_group_mod(datapath)            

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

