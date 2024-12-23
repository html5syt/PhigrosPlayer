import logging

import chartobj_rpe

def _controlevents(line: dict, controlName: str, svalName: str, tvalName: str):
    controlList: list[dict] = line.get(controlName, [])
    return [
        chartobj_rpe.ControlItem(
            sval = i.get(svalName, 0.0),
            tval = i.get(tvalName, 0.0),
            easing = i.get("easing", 0)
        )
        for i in controlList
    ]

def _lineevents(layer: dict|None, name: str):
    es: list[dict] = layer.get(name, []) if layer is not None else []
    return [
        chartobj_rpe.LineEvent(
            startTime = chartobj_rpe.Beat(*e.get("startTime", [0, 0, 1])),
            endTime = chartobj_rpe.Beat(*e.get("endTime", [0, 0, 1])),
            start = e.get("start", 0.0), end = e.get("end", 0.0),
            easingType = e.get("easingType", 1)
        ) for e in es
    ]

def _extendedevents(extended: dict, name: str, default: int|float|str|list[int]):
    es: list[dict] = extended.get(name, [])
    return [
        chartobj_rpe.LineEvent(
            startTime = chartobj_rpe.Beat(*e.get("startTime", [0, 0, 1])),
            endTime = chartobj_rpe.Beat(*e.get("endTime", [0, 0, 1])),
            start = e.get("start", default), end = e.get("end", default),
            easingType = e.get("easingType", 1)
        ) for e in es
    ]

def _extended(line: dict):
    extended_dict = line.get("extended", None)
    if extended_dict is None: return None
    
    return chartobj_rpe.Extended(
        scaleXEvents = _extendedevents(extended_dict, "scaleXEvents", 1.0),
        scaleYEvents = _extendedevents(extended_dict, "scaleYEvents", 1.0),
        colorEvents = _extendedevents(extended_dict, "colorEvents", [255, 255, 255]),
        textEvents = _extendedevents(extended_dict, "textEvents", ""),
    )

def Load_Chart_Object(chart: dict):
    logging.info("Loading Chart Object, fmt = rpe")
    meta = chart.get("META", {})
    rpe_chart_obj = chartobj_rpe.Rpe_Chart(
        META = chartobj_rpe.MetaData(
            RPEVersion = meta.get("RPEVersion", -1),
            offset = meta.get("offset", 0),
            name = meta.get("name", "Unknow"),
            id = meta.get("id", "-1"),
            song = meta.get("song", "Unknow"),
            background = meta.get("background", "Unknow"),
            composer = meta.get("composer", "Unknow"),
            charter = meta.get("charter", "Unknow"),
            level = meta.get("level", "Unknow"),
        ),
        BPMList = [
            chartobj_rpe.BPMEvent(
                startTime = chartobj_rpe.Beat(*bpme.get("startTime", [0, 0, 1])),
                bpm = bpme.get("bpm", 140)
            )
            for bpme in chart.get("BPMList", [])
        ],
        JudgeLineList = [
            chartobj_rpe.JudgeLine(
                isCover = line.get("isCover", 1),
                Texture = line.get("Texture", "line.png"),
                attachUI = line.get("attachUI", None),
                bpmfactor = line.get("bpmfactor", 1.0),
                father = line.get("father", -1),
                zOrder = line.get("zOrder", 0),
                eventLayers = [
                    chartobj_rpe.EventLayer(
                        speedEvents = _lineevents(layer, "speedEvents"),
                        moveXEvents = _lineevents(layer, "moveXEvents"),
                        moveYEvents = _lineevents(layer, "moveYEvents"),
                        rotateEvents = _lineevents(layer, "rotateEvents"),
                        alphaEvents = _lineevents(layer, "alphaEvents")
                    )
                    for layer in line.get("eventLayers", [])
                ],
                extended = _extended(line),
                notes = [
                    chartobj_rpe.Note(
                        type = n.get("type", 1),
                        startTime = chartobj_rpe.Beat(*n.get("startTime", [0, 0, 1])),
                        endTime = chartobj_rpe.Beat(*n.get("endTime", [0, 0, 1])),
                        positionX = n.get("positionX", 0),
                        above = n.get("above", 1),
                        isFake = n.get("isFake", False),
                        speed = n.get("speed", 1.0),
                        yOffset = n.get("yOffset", 0.0),
                        visibleTime = n.get("visibleTime", 999999.0),
                        width = n.get("size", 1.0),
                        alpha = n.get("alpha", 255),
                    )
                    for n in line.get("notes", [])
                ],
                controlEvents = chartobj_rpe.ControlEvents(
                    alphaControls = _controlevents(line, "alphaControl", "x", "alpha"),
                    posControls = _controlevents(line, "posControl", "x", "pos"),
                    sizeControls = _controlevents(line, "sizeControl", "x", "size"),
                    yControls = _controlevents(line, "yControl", "x", "y")
                )
            )
            for line in chart.get("judgeLineList", [])
        ]
    )
    
    logging.info("Finding Chart More Bets, fmt = rpe")

    def morebets_note(note: list[chartobj_rpe.Note]):
        times = {}
        
        for i in note:
            if i.startTime.value not in times: times[i.startTime.value] = 1
            else: times[i.startTime.value] += 1
            
        for i in note:
            if times[i.startTime.value] > 1:
                i.morebets = True

    all_notes = [note for line in rpe_chart_obj.JudgeLineList for note in line.notes]
    morebets_note([i for i in all_notes if not i.isFake])
    morebets_note([i for i in all_notes if i.isFake])
                
    logging.info("Load Chart Object Successfully, fmt = rpe")
    
    return rpe_chart_obj