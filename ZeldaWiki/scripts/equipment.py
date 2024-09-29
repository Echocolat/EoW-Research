import json

with open('ZeldaWiki/data/equipment.json', 'r') as json_file:
    equipment_data = json.loads(json_file.read())

def format_entry(entry):

    string = f"\n|style=\"text-align:center\"| {{{{Section|{entry['Name']}|[[File:EoW {entry['Name']} Icon.png|link={entry['Name']}]]<br/> '''{{{{Term|EoW|{entry['Name']}|link}}}}'''}}}}"
    string = string + f"\n|''\"{entry['Description'].replace('\n', ' ')}\"''"
    string = string + f"\n|style=\"text-align:center\"| {{{{Section|{entry['Effect Name']}|[[File:EoW {entry['Effect Name']} Icon.png|link={entry['Effect Name']}]]<br/> '''{{{{Term|EoW|{entry['Effect Name']}|link}}}}'''}}}}"
    string = string + f"\n|Fill Location here"

    return string

def generate_text_accessories():

    header = "{| class=\"wikitable\" style=\"width:50%; text-align:left;\"\n|-\n!width=10%| Accessory\n!width=20%| Description\n!width=15%| Effect\n!width=30%| Location"

    for key in equipment_data:

        if equipment_data[key]['Type'] == "Accessory":

            header = header + '\n|-' + format_entry(equipment_data[key])

    header = header + "\n|}"

    with open('ZeldaWiki/output/equipment.txt', 'w') as txt_file:
        txt_file.write(header)

generate_text_accessories()