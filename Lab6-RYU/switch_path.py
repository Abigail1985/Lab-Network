from ryu.controller import ofp_event
from ryu.lib import hub
from ryu.base import app_manager
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.controller import ofp_event 
from ryu.ofproto import ofproto_v1_3
 
class SwitchPath(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION] 
    def __init__(self, *args, **kwargs):
        super(SwitchPath, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.change_flow = hub.spawn(self._change_flow)

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                del self.datapaths[datapath.id]
 
    def _change_flow(self):
        flag = 1
 
        while True:
            print('datapath:', self.datapaths)
            try:
                if flag == 1:
                    print('flag:', flag)
                    flag = 2
                    self.match_flow(dpid=1, in_port=1, out_port=2, priority=1, add_del=0)
                    self.match_flow(dpid=1, in_port=2, out_port=1, priority=1, add_del=0)
 
                    self.match_flow(dpid=1, in_port=1, out_port=3, priority=1, add_del=1)
                    self.match_flow(dpid=1, in_port=3, out_port=1, priority=1, add_del=1)

                    self.match_flow(dpid=2, in_port=1, out_port=2, priority=1, add_del=0)
                    self.match_flow(dpid=2, in_port=2, out_port=1, priority=1, add_del=0)

                    self.match_flow(dpid=2, in_port=1, out_port=3, priority=1, add_del=1)
                    self.match_flow(dpid=2, in_port=3, out_port=1, priority=1, add_del=1)

                    self.match_flow(dpid=3, in_port=1, out_port=2, priority=1, add_del=0)
                    self.match_flow(dpid=3, in_port=2, out_port=1, priority=1, add_del=0)

                    self.match_flow(dpid=4, in_port=1, out_port=2, priority=1, add_del=1)
                    self.match_flow(dpid=4, in_port=2, out_port=1, priority=1, add_del=1)

 
                elif flag == 2:
                    print('flag:', flag)
                    flag = 1
                    self.match_flow(dpid=1, in_port=1, out_port=2, priority=1, add_del=1)
                    self.match_flow(dpid=1, in_port=2, out_port=1, priority=1, add_del=1)
 
                    self.match_flow(dpid=1, in_port=1, out_port=3, priority=1, add_del=0)
                    self.match_flow(dpid=1, in_port=3, out_port=1, priority=1, add_del=0)

                    self.match_flow(dpid=2, in_port=1, out_port=2, priority=1, add_del=1)
                    self.match_flow(dpid=2, in_port=2, out_port=1, priority=1, add_del=1)

                    self.match_flow(dpid=2, in_port=1, out_port=3, priority=1, add_del=0)
                    self.match_flow(dpid=2, in_port=3, out_port=1, priority=1, add_del=0)

                    self.match_flow(dpid=3, in_port=1, out_port=2, priority=1, add_del=1)
                    self.match_flow(dpid=3, in_port=2, out_port=1, priority=1, add_del=1)

                    self.match_flow(dpid=4, in_port=1, out_port=2, priority=1, add_del=0)
                    self.match_flow(dpid=4, in_port=2, out_port=1, priority=1, add_del=0)

            except Exception as info:
                print('info:', info)
 
            hub.sleep(5)
 
 
    def match_flow(self, dpid, in_port, out_port, priority, add_del):
        parser = self.datapaths[dpid].ofproto_parser
        ofp = self.datapaths[dpid].ofproto
        actions = [parser.OFPActionOutput(out_port)]
        if add_del == 1:
            match = parser.OFPMatch(in_port=in_port)
            self.add_flow(datapath=self.datapaths[dpid], priority=priority, match=match, actions=actions)
        if add_del == 0:
            match = parser.OFPMatch()
            self.del_flow(datapath=self.datapaths[dpid], match=match)
 
    def del_flow(self, datapath, match):
        ofp = datapath.ofproto
        parser = datapath.ofproto_parser
 
        req = parser.OFPFlowMod(datapath=datapath,
                                    command=ofp.OFPFC_DELETE,
                                    out_port=ofp.OFPP_ANY,
                                    out_group=ofp.OFPG_ANY,
                                    match=match)
        datapath.send_msg(req)
 
    def add_flow(self, datapath, priority, match, actions):
        ofp = datapath.ofproto
        parser = datapath.ofproto_parser
        command = ofp.OFPFC_ADD
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        req = parser.OFPFlowMod(datapath=datapath, command=command,
                                    priority=priority, match=match, instructions=inst)
        datapath.send_msg(req)

