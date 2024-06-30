# i can't write this file, because i don't know rpe format... how can help me?????????  welcome to my github to create a issue. thank you very much!!!
# why lchzh3427`s player can`t play it?
from sys import argv
from dataclasses import dataclass
from functools import cache
import json
import math
import typing

import Chart_Functions_Rep
import Chart_Objects_Rep
import rpe2phi_moveNode_hashConst

with open(argv[1],"r",encoding="utf-8") as f:
    rpe_obj = Chart_Functions_Rep.Load_Chart_Object(json.load(f))

ease_funcs = [
  lambda t: t, # linear - 1
  lambda t: math.sin((t * math.pi) / 2), # out sine - 2
  lambda t: 1 - math.cos((t * math.pi) / 2), # in sine - 3
  lambda t: 1 - (1 - t) * (1 - t), # out quad - 4
  lambda t: t ** 2, # in quad - 5
  lambda t: -(math.cos(math.pi * t) - 1) / 2, # io sine - 6
  lambda t: 2 * (t ** 2) if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2, # io quad - 7
  lambda t: 1 - (1 - t) ** 3, # out cubic - 8
  lambda t: t ** 3, # in cubic - 9
  lambda t: 1 - (1 - t) ** 4, # out quart - 10
  lambda t: t ** 4, # in quart - 11
  lambda t: 4 * (t ** 3) if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2, # io cubic - 12
  lambda t: 8 * (t ** 4) if t < 0.5 else 1 - (-2 * t + 2) ** 4 / 2, # io quart - 13
  lambda t: 1 - (1 - t) ** 5, # out quint - 14
  lambda t: t ** 5, # in quint - 15
  lambda t: 1 if t == 1 else 1 - 2 ** (-10 * t), # out expo - 16
  lambda t: 0 if t == 0 else 2 ** (10 * t - 10), # in expo - 17
  lambda t: (1 - (t - 1) ** 2) ** 0.5, # out circ - 18
  lambda t: 1 - (1 - t ** 2) ** 0.5, # in circ - 19
  lambda t: 1 + 2.70158 * ((t - 1) ** 3) + 1.70158 * ((t - 1) ** 2), # out back - 20
  lambda t: 2.70158 * (t ** 3) - 1.70158 * (t ** 2), # in back - 21
  lambda t: (1 - (1 - (2 * t) ** 2) ** 0.5) / 2 if t < 0.5 else (((1 - (-2 * t + 2) ** 2) ** 0.5) + 1) / 2, # io circ - 22
  lambda t: ((2 * t) ** 2 * ((2.5949095 + 1) * 2 * t - 2.5949095)) / 2 if t < 0.5 else ((2 * t - 2) ** 2 * ((2.5949095 + 1) * (t * 2 - 2) + 2.5949095) + 2) / 2, # io back - 23
  lambda t: 0 if t == 0 else (1 if t == 1 else 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi / 3)) + 1), # out elastic - 24
  lambda t: 0 if t == 0 else (1 if t == 1 else - 2 ** (10 * t - 10) * math.sin((t * 10 - 10.75) * (2 * math.pi / 3))), # in elastic - 25
  lambda t: 7.5625 * (t ** 2) if (t < 1 / 2.75) else (7.5625 * (t - (1.5 / 2.75)) * (t - (1.5 / 2.75)) + 0.75 if (t < 2 / 2.75) else (7.5625 * (t - (2.25 / 2.75)) * (t - (2.25 / 2.75)) + 0.9375 if (t < 2.5 / 2.75) else (7.5625 * (t - (2.625 / 2.75)) * (t - (2.625 / 2.75)) + 0.984375))), # out bounce - 26
  lambda t: 1 - ease_funcs[26 - 1](1 - t), # in bounce - 27
  lambda t: (1 - ease_funcs[26 - 1](1 - 2 * t)) / 2 if t < 0.5 else (1 + ease_funcs[26 - 1](2 * t - 1)) / 2, # io bounce - 28
  lambda t: 0 if t == 0 else (1 if t == 0 else (-2 ** (20 * t - 10) * math.sin((20 * t - 11.125) * ((2 * math.pi) / 4.5))) / 2 if t < 0.5 else (2 ** (-20 * t + 10) * math.sin((20 * t - 11.125) * ((2 * math.pi) / 4.5))) / 2 + 1) # io elastic - 29
]

@dataclass
class Move:
    type: typing.Literal["x", "y"]
    st: float
    et: float
    sv: float
    ev: float

@dataclass
class PhiMove:
    st: float
    et: float
    sv_x: float
    sv_y: float
    ev_x: float
    ev_y: float

@dataclass
class RpeMoveNode:
    item: Move
    type: typing.Literal["start", "end"]
    value: float

@dataclass
class MoveEventManager:
    moves: typing.List[Move]
    nodes: typing.List[RpeMoveNode]
    
    def __post_init__(self):
        for e in moves:
            self.nodes.append(
                    RpeMoveNode(
                    item = e,
                    type = "start",
                    value = e.st
                )
            )
            self.nodes.append(
                    RpeMoveNode(
                    item = e,
                    type = "end",
                    value = e.et
                )
            )
        
        self.nodes.sort(key = lambda x: x.value)

phi_data = {
    "formatVersion": 3,
    "offset": rpe_obj.META.offset / 1000,
    "judgeLineList" :[]
}

split_event_length = 25
T = 1.875 / rpe_obj.BPMList[0].bpm

for index,bpm in enumerate(rpe_obj.BPMList):
    if index != len(rpe_obj.BPMList) - 1:
        next_bpm = rpe_obj.BPMList[index + 1]
        bpm.dur = next_bpm.startTime.value - bpm.startTime.value
    else:
        bpm.dur = float("inf")

@cache
def getReal(b:Chart_Objects_Rep.Beat):
    realtime = 0.0
    for bpm in rpe_obj.BPMList:
        if bpm.startTime.value < b.value:
            if bpm.startTime.value + bpm.dur > b.value:
                realtime += 60 / bpm.bpm * (b.value - bpm.startTime.value)
            else:
                realtime += 60 / bpm.bpm * bpm.dur
    return realtime

@cache
def linear_interpolation(
    t:float,
    st:float,
    et:float,
    sv:float,
    ev:float
) -> float:
    if t == st: return sv
    return (t - st) / (et - st) * (ev - sv) + sv

def get_phimove_state_x(t):
    for move in moves:
        if move.st <= t <= move.et:
            if move.type == "x":
                return linear_interpolation(t, move.st, move.et, move.sv, move.ev)

def get_phimove_state_y(t):
    for move in moves:
        if move.st <= t <= move.et:
            if move.type == "y":
                return linear_interpolation(t, move.st, move.et, move.sv, move.ev)

def get_floor_position(t):
    v = 0.0
    for e in phi_judgeLine["speedEvents"]:
        if e["startTime"] < t < e["endTime"]:
            v += (t - e["startTime"]) * T * e["value"]
        elif e["endTime"] <= t:
            v += (e["endTime"] - e["startTime"]) * T * e["value"]
    return v

def get_speed(t):
    for e in phi_judgeLine["speedEvents"]:
        if e["startTime"] <= t <= e["endTime"]:
            return e["value"]
    return 1.0

@cache
def conv_note(n):
    return {1:1, 2:3, 3:4, 4:2}[n]

for rpe_judgeLine in rpe_obj.JudgeLineList:
    phi_judgeLine = {
        "bpm": rpe_obj.BPMList[0].bpm,
        "notesAbove": [],
        "notesBelow": [],
        "speedEvents": [],
        "judgeLineMoveEvents": [],
        "judgeLineRotateEvents": [],
        "judgeLineDisappearEvents": []
    }
    
    moves:typing.List[Move] = []
    
    for eventLayer in rpe_judgeLine.eventLayers:
        if eventLayer.alphaEvents is not None:
            for e in eventLayer.alphaEvents:
                st = getReal(e.startTime)
                et = getReal(e.endTime)
                sv = (255 & e.start) / 255
                ev = (255 & e.end) / 255
                ef = ease_funcs[e.easingType - 1]
                for i in range(split_event_length):
                    ist = st + i * (et - st) / split_event_length
                    iet = st + (i + 1) * (et - st) / split_event_length
                    isvp = ef(i / split_event_length)
                    ievp = ef((i + 1) / split_event_length)
                    isv = linear_interpolation(isvp, 0.0, 1.0, sv, ev)
                    iev = linear_interpolation(ievp, 0.0, 1.0, sv, ev)
                    phi_judgeLine["judgeLineDisappearEvents"].append(
                        {
                            "startTime": ist / T,
                            "endTime": iet / T,
                            "start": isv,
                            "end": iev
                        }
                    )
        
        if eventLayer.rotateEvents is not None:
            for e in eventLayer.rotateEvents:
                st = getReal(e.startTime)
                et = getReal(e.endTime)
                sv = - e.start
                ev = - e.end
                ef = ease_funcs[e.easingType - 1]
                for i in range(split_event_length):
                    ist = st + i * (et - st) / split_event_length
                    iet = st + (i + 1) * (et - st) / split_event_length
                    isvp = ef(i / split_event_length)
                    ievp = ef((i + 1) / split_event_length)
                    isv = linear_interpolation(isvp, 0.0, 1.0, sv, ev)
                    iev = linear_interpolation(ievp, 0.0, 1.0, sv, ev)
                    phi_judgeLine["judgeLineRotateEvents"].append(
                        {
                            "startTime": ist / T,
                            "endTime": iet / T,
                            "start": isv,
                            "end": iev
                        }
                    )
        
        if eventLayer.moveXEvents is not None:
            for e in eventLayer.moveXEvents:
                st = getReal(e.startTime)
                et = getReal(e.endTime)
                sv = e.start
                ev = e.end
                ef = ease_funcs[e.easingType - 1]
                for i in range(split_event_length):
                    ist = st + i * (et - st) / split_event_length
                    iet = st + (i + 1) * (et - st) / split_event_length
                    isvp = ef(i / split_event_length)
                    ievp = ef((i + 1) / split_event_length)
                    isv = linear_interpolation(isvp, 0.0, 1.0, sv, ev)
                    iev = linear_interpolation(ievp, 0.0, 1.0, sv, ev)
                    moves.append(
                        Move(
                            type = "x",
                            st = ist / T,
                            et = iet / T,
                            sv = (isv + 675) / 1350,
                            ev = (iev + 675) / 1350
                        )
                    )
        
        if eventLayer.moveYEvents is not None:
            for e in eventLayer.moveYEvents:
                st = getReal(e.startTime)
                et = getReal(e.endTime)
                sv = e.start
                ev = e.end
                ef = ease_funcs[e.easingType - 1]
                for i in range(split_event_length):
                    ist = st + i * (et - st) / split_event_length
                    iet = st + (i + 1) * (et - st) / split_event_length
                    isvp = ef(i / split_event_length)
                    ievp = ef((i + 1) / split_event_length)
                    isv = linear_interpolation(isvp, 0.0, 1.0, sv, ev)
                    iev = linear_interpolation(ievp, 0.0, 1.0, sv, ev)
                    moves.append(
                        Move(
                            type = "y",
                            st = ist / T,
                            et = iet / T,
                            sv = (isv + 450) / 900,
                            ev = (iev + 450) / 900
                        )
                    )
        
        if eventLayer.speedEvents is not None:
            for e in eventLayer.speedEvents:
                st = getReal(e.startTime)
                et = getReal(e.endTime)
                v = (e.start + e.end) / 2 # normal, e.start == e.end is True
                phi_judgeLine["speedEvents"].append(
                    {
                        "startTime": st / T,
                        "endTime": et / T,
                        "value": (v * 120) / 900 / 0.6
                    }
                )
    
    if len(phi_judgeLine["speedEvents"]) > 0:
        phi_judgeLine["speedEvents"].sort(key = lambda x: x["endTime"])
        phi_judgeLine["speedEvents"][-1]["endTime"] = 1000000000
        min_st = (float("inf"), None)
        for e in phi_judgeLine["speedEvents"]:
            if e["startTime"] < min_st[0]:
                min_st = (e["startTime"], e)
        min_st[1]["startTime"] = -999999
        
        for index, e in enumerate(phi_judgeLine["speedEvents"]):
            if index == len(phi_judgeLine["speedEvents"]) - 1:
                break
            else:
                ne = phi_judgeLine["speedEvents"][index + 1]
                if e["endTime"] != ne["startTime"]:
                    e["endTime"] = ne["startTime"]
        
    if len(phi_judgeLine["judgeLineDisappearEvents"]) > 0:
        phi_judgeLine["judgeLineDisappearEvents"].sort(key = lambda x: x["endTime"])
        phi_judgeLine["judgeLineDisappearEvents"][-1]["endTime"] = 1000000000
        min_st = (float("inf"), None)
        for e in phi_judgeLine["judgeLineDisappearEvents"]:
            if e["startTime"] < min_st[0]:
                min_st = (e["startTime"], e)
        min_st[1]["startTime"] = -999999
        
        oth_es = []
        for index, e in enumerate(phi_judgeLine["judgeLineDisappearEvents"]):
            if index == len(phi_judgeLine["judgeLineDisappearEvents"]) - 1:
                break
            else:
                ne = phi_judgeLine["judgeLineDisappearEvents"][index + 1]
                if e["endTime"] < ne["startTime"]:
                    oth_es.append({
                        "startTime": e["endTime"],
                        "endTime": ne["startTime"],
                        "start": e["end"],
                        "end": e["end"]
                    })
        phi_judgeLine["judgeLineDisappearEvents"] += oth_es
    
    if len(phi_judgeLine["judgeLineRotateEvents"]) > 0:
        phi_judgeLine["judgeLineRotateEvents"].sort(key = lambda x: x["endTime"])
        phi_judgeLine["judgeLineRotateEvents"][-1]["endTime"] = 1000000000
        min_st = (float("inf"), None)
        for e in phi_judgeLine["judgeLineRotateEvents"]:
            if e["startTime"] < min_st[0]:
                min_st = (e["startTime"], e)
        min_st[1]["startTime"] = -999999
        
        oth_es = []
        for index, e in enumerate(phi_judgeLine["judgeLineRotateEvents"]):
            if index == len(phi_judgeLine["judgeLineRotateEvents"]) - 1:
                break
            else:
                ne = phi_judgeLine["judgeLineRotateEvents"][index + 1]
                if e["endTime"] < ne["startTime"]:
                    oth_es.append({
                        "startTime": e["endTime"],
                        "endTime": ne["startTime"],
                        "start": e["end"],
                        "end": e["end"]
                    })
        phi_judgeLine["judgeLineRotateEvents"] += oth_es
    
    for note in rpe_judgeLine.notes: # has bugsssssssss
        st = getReal(note.startTime)
        et = getReal(note.endTime)
        phi_judgeLine["notesAbove"]
        item = {
            "type": conv_note(note.type),
            "time": st / T,
            "holdTime": (et - st) / T,
            "positionX": note.positionX / 1350 / 0.05625,
            "speed": ((get_floor_position(et / T) - get_floor_position(st / T)) / ((et - st) / T)) / T if et != st else get_speed(st),
            "floorPosition": get_floor_position(st / T)
        }
        if note.above:
            phi_judgeLine["notesAbove"].append(item)
        else:
            phi_judgeLine["notesBelow"].append(item)
            
            
    MoveEventMgr_Object = MoveEventManager(moves, [])
    
    for index, this_node in enumerate(MoveEventMgr_Object.nodes):
        if index != len(MoveEventMgr_Object.nodes) - 1:
            next_node = MoveEventMgr_Object.nodes[index + 1]
            
            if this_node.value == next_node.value:
                continue
            
            two_node_hash = hash(((this_node.item.type, this_node.type), (next_node.item.type, next_node.type)))
            
            match two_node_hash: # uueee.
                case rpe2phi_moveNode_hashConst.LEFT_START_X__RIGHT_START_Y:
                    phi_judgeLine["judgeLineMoveEvents"].append({
                        "startTime": this_node.item.st,
                        "endTime": next_node.item.et,
                        "start": this_node.item.sv,
                        "end": get_phimove_state_x(next_node.item.st),
                        "start2": get_phimove_state_y(this_node.item.st),
                        "end2": next_node.item.sv
                    })
                case rpe2phi_moveNode_hashConst.LEFT_START_X__RIGHT_END_Y:
                    phi_judgeLine["judgeLineMoveEvents"].append({
                        "startTime": this_node.item.st,
                        "endTime": next_node.item.et,
                        "start": this_node.item.sv,
                        "end": get_phimove_state_x(next_node.item.et),
                        "start2": get_phimove_state_y(this_node.item.st),
                        "end2": next_node.item.sv
                    })
                case rpe2phi_moveNode_hashConst.LEFT_END_X__RIGHT_START_Y:
                    phi_judgeLine["judgeLineMoveEvents"].append({
                        "startTime": this_node.item.et,
                        "endTime": next_node.item.st,
                        "start": this_node.item.ev,
                        "end": get_phimove_state_x(next_node.item.st),
                        "start2": get_phimove_state_y(this_node.item.et),
                        "end2": next_node.item.sv
                    })
                case rpe2phi_moveNode_hashConst.LEFT_END_X__RIGHT_END_Y:
                    phi_judgeLine["judgeLineMoveEvents"].append({
                        "startTime": this_node.item.et,
                        "endTime": next_node.item.et,
                        "start": this_node.item.ev,
                        "end": get_phimove_state_x(next_node.item.et),
                        "start2": get_phimove_state_y(this_node.item.et),
                        "end2": next_node.item.ev
                    })
                case rpe2phi_moveNode_hashConst.LEFT_START_Y__RIGHT_START_X:
                    phi_judgeLine["judgeLineMoveEvents"].append({
                        "startTime": this_node.item.st,
                        "endTime": next_node.item.st,
                        "start": this_node.item.sv,
                        "end": get_phimove_state_x(next_node.item.st),
                        "start2": this_node.item.sv,
                        "end2": get_phimove_state_y(next_node.item.st)
                    })
                case rpe2phi_moveNode_hashConst.LEFT_START_Y__RIGHT_END_X:
                    phi_judgeLine["judgeLineMoveEvents"].append({
                        "startTime": this_node.item.st,
                        "endTime": next_node.item.et,
                        "start": get_phimove_state_x(this_node.item.st),
                        "end": next_node.item.ev,
                        "start2": this_node.item.sv,
                        "end2": get_phimove_state_y(next_node.item.et)
                    })
                case rpe2phi_moveNode_hashConst.LEFT_END_Y__RIGHT_START_X:
                    phi_judgeLine["judgeLineMoveEvents"].append({
                        "startTime": this_node.item.et,
                        "endTime": next_node.item.st,
                        "start": get_phimove_state_x(this_node.item.et),
                        "end": next_node.item.ev,
                        "start2": this_node.item.ev,
                        "end2": get_phimove_state_y(next_node.item.st)
                    })
                case rpe2phi_moveNode_hashConst.LEFT_END_Y__RIGHT_END_X:
                    phi_judgeLine["judgeLineMoveEvents"].append({
                        "startTime": this_node.item.et,
                        "endTime": next_node.item.et,
                        "start": get_phimove_state_x(this_node.item.et),
                        "end": next_node.item.ev,
                        "start2": this_node.item.ev,
                        "end2": get_phimove_state_y(next_node.item.et)
                    })
                case rpe2phi_moveNode_hashConst.LEFT_START_X__RIGHT_START_X: # never
                    phi_judgeLine["judgeLineMoveEvents"].append({
                        "startTime": this_node.item.st,
                        "endTime": next_node.item.st,
                        "start": this_node.item.sv,
                        "end": next_node.item.sv,
                        "start2": get_phimove_state_y(this_node.item.st),
                        "end2": get_phimove_state_y(next_node.item.st)
                    })
                case rpe2phi_moveNode_hashConst.LEFT_START_X__RIGHT_END_X:
                    phi_judgeLine["judgeLineMoveEvents"].append({
                        "startTime": this_node.item.st,
                        "endTime": next_node.item.et,
                        "start": this_node.item.sv,
                        "end": next_node.item.ev,
                        "start2": get_phimove_state_y(this_node.item.st),
                        "end2": get_phimove_state_y(next_node.item.et)
                    })
                case rpe2phi_moveNode_hashConst.LEFT_END_X__RIGHT_START_X:
                    phi_judgeLine["judgeLineMoveEvents"].append({
                        "startTime": this_node.item.et,
                        "endTime": next_node.item.st,
                        "start": this_node.item.ev,
                        "end": next_node.item.sv,
                        "start2": get_phimove_state_y(this_node.item.et),
                        "end2": get_phimove_state_y(next_node.item.st)
                    })
                case rpe2phi_moveNode_hashConst.LEFT_END_X__RIGHT_END_X: # never
                    phi_judgeLine["judgeLineMoveEvents"].append({
                        "startTime": this_node.item.et,
                        "endTime": next_node.item.et,
                        "start": this_node.item.ev,
                        "end": next_node.item.ev,
                        "start2": get_phimove_state_y(this_node.item.et),
                        "end2": get_phimove_state_y(next_node.item.et)
                    })
                case rpe2phi_moveNode_hashConst.LEFT_START_Y__RIGHT_START_Y: # never
                    phi_judgeLine["judgeLineMoveEvents"].append({
                        "startTime": this_node.item.st,
                        "endTime": next_node.item.st,
                        "start": get_phimove_state_x(this_node.item.st),
                        "end": get_phimove_state_x(next_node.item.st),
                        "start2": this_node.item.sv,
                        "end2": next_node.item.sv
                    })
                case rpe2phi_moveNode_hashConst.LEFT_START_Y__RIGHT_END_Y:
                    phi_judgeLine["judgeLineMoveEvents"].append({
                        "startTime": this_node.item.st,
                        "endTime": next_node.item.et,
                        "start": get_phimove_state_x(this_node.item.st),
                        "end": get_phimove_state_x(next_node.item.et),
                        "start2": this_node.item.sv,
                        "end2": next_node.item.ev
                    })
                case rpe2phi_moveNode_hashConst.LEFT_END_Y__RIGHT_START_Y:
                    phi_judgeLine["judgeLineMoveEvents"].append({
                        "startTime": this_node.item.et,
                        "endTime": next_node.item.st,
                        "start": get_phimove_state_x(this_node.item.et),
                        "end": get_phimove_state_x(next_node.item.st),
                        "start2": this_node.item.ev,
                        "end2": next_node.item.sv
                    })
                case rpe2phi_moveNode_hashConst.LEFT_END_Y__RIGHT_END_Y: # never
                    phi_judgeLine["judgeLineMoveEvents"].append({
                        "startTime": this_node.item.et,
                        "endTime": next_node.item.et,
                        "start": get_phimove_state_x(this_node.item.et),
                        "end": get_phimove_state_x(next_node.item.et),
                        "start2": this_node.item.ev,
                        "end2": next_node.item.ev,
                    })
                case _:
                    print(f"Warning: Never! {this_node, next_node} hash-{two_node_hash}.")
    
    if len(phi_judgeLine["judgeLineMoveEvents"]) > 0:
        phi_judgeLine["judgeLineMoveEvents"].sort(key = lambda x: x["endTime"])
        phi_judgeLine["judgeLineMoveEvents"][-1]["endTime"] = 1000000000
        min_st = (float("inf"), None)
        for e in phi_judgeLine["judgeLineMoveEvents"]:
            if e["startTime"] < min_st[0]:
                min_st = (e["startTime"], e)
        min_st[1]["startTime"] = -999999
        
        oth_es = []
        for index, e in enumerate(phi_judgeLine["judgeLineMoveEvents"]):
            if index == len(phi_judgeLine["judgeLineMoveEvents"]) - 1:
                break
            else:
                ne = phi_judgeLine["judgeLineMoveEvents"][index + 1]
                if e["endTime"] < ne["startTime"]:
                    oth_es.append({
                        "startTime": e["endTime"],
                        "endTime": ne["startTime"],
                        "start": e["end"],
                        "end": e["end"],
                        "start2": e["end2"],
                        "end2": e["end2"]
                    })
        phi_judgeLine["judgeLineMoveEvents"] += oth_es
                    
    phi_data["judgeLineList"].append(phi_judgeLine)

with open(argv[2],"w",encoding="utf-8") as f:
    f.write(json.dumps(phi_data,ensure_ascii=False))