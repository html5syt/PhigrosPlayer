from __future__ import annotations
from dataclasses import dataclass
import typing

import Const
import Tool_Functions

NAN = float("NaN")

@dataclass
class note:
    type:typing.Literal[1,2,3,4]
    time:typing.Union[int,float]
    positionX:typing.Union[int,float]
    holdTime:typing.Union[int,float]
    speed:typing.Union[int,float]
    floorPosition:typing.Union[int,float]
    clicked:bool
    morebets:bool
    id:int
    rendered:bool
    by_judgeLine_id:int
    effect_random_blocks:typing.Tuple[int,int,int,int]
    master:typing.Union[judgeLine,None] = None
    hold_end_clicked:bool = False
    note_last_show_hold_effect_time:float = 0.0
    is_will_click:bool = False
    hold_click_type:typing.Union[None,typing.Literal["Perfect","Good"]] = None
    
    def __eq__(self,oth):
        try:
            return self.id == oth.id
        except AttributeError:
            return False

    def __hash__(self):
        return self.id
    
    def __repr__(self):
        note_t = {
            Const.Note.TAP:"t",
            Const.Note.DRAG:"d",
            Const.Note.HOLD:"h",
            Const.Note.FLICK:"f"
        }[self.type]
        return f"{self.master.id}+{self.by_judgeLine_id}{note_t}"
    
    def _cal_holdlength(self,PHIGROS_Y):
        self.hold_length_sec = self.holdTime * (1.875 / self.master.bpm)
        self.hold_length_px = (self.speed * self.hold_length_sec) * PHIGROS_Y
        self.hold_endtime = self.time * (1.875 / self.master.bpm) + self.hold_length_sec
        
        #do other... hehehehe
        self.effect_times = []
        hold_starttime = self.time * (1.875 / self.master.bpm)
        hold_effect_blocktime = (1 / self.master.bpm * 30)
        while True:
            hold_starttime += hold_effect_blocktime
            if hold_starttime >= self.hold_endtime:
                break
            self.effect_times.append((hold_starttime,Tool_Functions.get_effect_random_blocks()))

@dataclass
class speedEvent:
    startTime:typing.Union[int,float]
    endTime:typing.Union[int,float]
    value:typing.Union[int,float]
    floorPosition:typing.Union[typing.Union[int,float],None]

@dataclass
class judgeLineMoveEvent:
    startTime:typing.Union[int,float]
    endTime:typing.Union[int,float]
    start:typing.Union[int,float]
    end:typing.Union[int,float]
    start2:typing.Union[int,float]
    end2:typing.Union[int,float]

@dataclass
class judgeLineRotateEvent:
    startTime:typing.Union[int,float]
    endTime:typing.Union[int,float]
    start:typing.Union[int,float]
    end:typing.Union[int,float]

@dataclass
class judgeLineDisappearEvent:
    startTime:typing.Union[int,float]
    endTime:typing.Union[int,float]
    start:typing.Union[int,float]
    end:typing.Union[int,float]

@dataclass
class judgeLine:
    id:int
    bpm:typing.Union[int,float]
    notesAbove:list[note]
    notesBelow:list[note]
    speedEvents:list[speedEvent]
    judgeLineMoveEvents:list[judgeLineMoveEvent]
    judgeLineRotateEvents:list[judgeLineRotateEvent]
    judgeLineDisappearEvents:list[judgeLineDisappearEvent]

    def __eq__(self,oth):
        try:
            return self.id == oth.id
        except AttributeError:
            return False

    def __hash__(self):
        return self.id
    
    def __repr__(self):
        return f"JudgeLine-{self.id}"
    
    def set_master_to_notes(self):
        for note in self.notesAbove:
            note.master = self
        for note in self.notesBelow:
            note.master = self
    
    def get_datavar_rotate(self,now_time):
        for rotate_event in self.judgeLineRotateEvents:
            if rotate_event.startTime <= now_time <= rotate_event.endTime:
                try:
                    return rotate_event.start + (rotate_event.end - rotate_event.start) * ((now_time - rotate_event.startTime) / (rotate_event.endTime - rotate_event.startTime))
                except ZeroDivisionError:
                    return rotate_event.start
        return NAN
    
    def get_datavar_disappear(self,now_time):
        for disappear_event in self.judgeLineDisappearEvents:
            if disappear_event.startTime <= now_time <= disappear_event.endTime:
                try:
                    return disappear_event.start + (disappear_event.end - disappear_event.start) * ((now_time - disappear_event.startTime) / (disappear_event.endTime - disappear_event.startTime)) 
                except ZeroDivisionError:
                    return disappear_event.start
        return NAN
    
    def get_datavar_move(self,now_time,w,h):
        for move_event in self.judgeLineMoveEvents:
            if move_event.startTime <= now_time <= move_event.endTime:
                try:
                    r = [
                        move_event.start + (move_event.end - move_event.start) * ((now_time - move_event.startTime) / (move_event.endTime - move_event.startTime)),
                        move_event.start2 + (move_event.end2 - move_event.start2) * ((now_time - move_event.startTime) / (move_event.endTime - move_event.startTime))
                    ]
                    r = [r[0] * w,r[1] * h]
                except ZeroDivisionError:
                    r = [move_event.start * w,move_event.start2 * h]
                r[1] = h - r[1]
                return r
        return NAN

    def get_datavar_speed(self,now_time):
        for speed_event in self.speedEvents:
            if speed_event.startTime <= now_time <= speed_event.endTime:
               return speed_event.value
        return NAN

@dataclass
class Phigros_Chart:
    formatVersion:int
    offset:typing.Union[int,float]
    judgeLineList:list[judgeLine]

    def cal_note_num(self):
        self.note_num = 0
        for judgeLine in self.judgeLineList:
            for _ in judgeLine.notesAbove:
                self.note_num += 1
            for _ in judgeLine.notesBelow:
                self.note_num += 1
    
    def init_holdlength(self,PHIGROS_Y):
        for judgeLine in self.judgeLineList:
            for note in judgeLine.notesAbove:
                note._cal_holdlength(PHIGROS_Y)
            for note in judgeLine.notesBelow:
                note._cal_holdlength(PHIGROS_Y)
    
    def get_all_note(self) -> list[note]:
       return [j for i in self.judgeLineList for j in i.notesAbove + i.notesBelow]

del typing,dataclass