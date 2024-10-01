import json

with open('Bidouillage events/Untouched/MapWarp.json', 'r') as json_file:
    map_warp_base = json.loads(json_file.read())

with open('Bidouillage events/waypoints.json', 'r') as json_file:
    waypoints = json.loads(json_file.read())

def edit():

    base_event_index = 123
    base_event_name = 131

    for waypoint in waypoints:

        query = {
                    "ActorIndex": 7,
                    "ActorQueryIndex": 0,
                    "Parameters": {
                        "value1": {
                            "Argument": "locator"
                        },
                        "value2": {
                            "String": waypoints[waypoint]['mLocation']
                        }
                    },
                    "SwitchCases": [
                        {
                            "Value": 0,
                            "EventIndex": base_event_index + 1
                        },
                        {
                            "Value": 1,
                            "EventIndex": base_event_index + 2
                        }
                    ],
                    "ActorName": "FlowControl",
                    "ActorQuery": "CompareString",
                    "Name": f"Event{base_event_name}",
                    "Type": "Switch"
                }
        
        base_event_name += 1
        base_event_index += 1

        show = {
                "NextEventIndex": 43,
                "ActorIndex": 9,
                "ActorActionIndex": 0,
                "Parameters": {
                "message": {
                        "String": f"Signboard:{waypoints[waypoint]['mLocation']}"
                    }
                },
                "NextEventName": "Event17",
                "ActorName": "Dialog",
                "ActorAction": "Show",
                "Name": f"Event{base_event_name}",
                "Type": "Action"
            }
        
        base_event_name += 1
        base_event_index += 1
        
        map_warp_base['Flowcharts']['MapWarp']['Events'].append(query)
        map_warp_base['Flowcharts']['MapWarp']['Events'].append(show)

    base_event_index = 123
    base_event_name = 131

    for waypoint in waypoints:

        query = {
                    "ActorIndex": 7,
                    "ActorQueryIndex": 0,
                    "Parameters": {
                        "value1": {
                            "Argument": "locator"
                        },
                        "value2": {
                            "String": waypoints[waypoint]['mLocation']
                        }
                    },
                    "SwitchCases": [
                        {
                            "Value": 0,
                            "EventIndex": base_event_index + 1
                        },
                        {
                            "Value": 1,
                            "EventIndex": base_event_index + 2
                        }
                    ],
                    "ActorName": "FlowControl",
                    "ActorQuery": "CompareString",
                    "Name": f"Event{base_event_name}",
                    "Type": "Switch"
                }
        
        base_event_name += 1
        base_event_index += 1

        show = {
                "NextEventIndex": 43,
                "ActorIndex": 9,
                "ActorActionIndex": 0,
                "Parameters": {
                "message": {
                        "String": f"Signboard:{waypoints[waypoint]['mLocation']}"
                    }
                },
                "NextEventName": "Event17",
                "ActorName": "Dialog",
                "ActorAction": "Show",
                "Name": f"Event{base_event_name}",
                "Type": "Action"
            }
        
        base_event_name += 1
        base_event_index += 1
        
        map_warp_base['Flowcharts']['MapWarp']['Events'].append(query)
        map_warp_base['Flowcharts']['MapWarp']['Events'].append(show)

    with open('Bidouillage events/Edited/MapWarp.json', 'w') as json_file:
        json_file.write(json.dumps(map_warp_base, indent = 2))

def do_text():

    full_text = ''
    base_text_id = 269

    for waypoint in waypoints:

        text = f"""---
label: {waypoints[waypoint]['mLocation']}
attribute: 0x06{str(hex(base_text_id)).replace("0x", '')[1:].upper() + "01"}0000000101
styleIndex: 1
---
Warping to {waypoints[waypoint]['mLocation']} (ID {waypoints[waypoint]['mReportId']})\nin {waypoints[waypoint]['mLevelName']}{{{{KeyWait}}}}

"""
        base_text_id += 1
        full_text = full_text + text

    with open('Bidouillage events/txt.txt', 'w') as txt_file:
        txt_file.write(full_text)

edit()