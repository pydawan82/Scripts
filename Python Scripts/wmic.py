import subprocess as sp

class WmiObject:
    wmi_class: str
    _properties: dict[str, str]

    def __init__(self, wmi_class, wmi_object):
        self.wmi_class = wmi_class
        self._properties = wmi_object

    def __getattr__(self, name: str):
        return self._properties[name.lower()]

    def __repr__(self):
        return f"{self.wmi_class}({self.wmi_object})"

def parse_wmic_output(wmi_class: str, output: str) -> list[WmiObject]:
    lines = output.splitlines()
    properties = [p.strip() for p in lines[0].split("  ") if p]
    objects_lines = lines[2::2]
    objects_lines = [l for l in objects_lines if l.strip()]
    wmi_objects = [dict() for _ in range(len(objects_lines))]

    pos = 0
    for prop in properties:
        prop = prop.lower()
        max_len = len(prop)
        for i, obj in enumerate(wmi_objects):
            obj[prop] = objects_lines[i][pos:].split("  ")[0]
            max_len = max(max_len, len(obj[prop]))
            if obj[prop] == "":
                del obj[prop]
        pos += max_len + 2

    return [WmiObject(wmi_class, obj) for obj in wmi_objects]

def wmic_get(wmi_class: str, *properties: list[str]) -> list[WmiObject]:
    return parse_wmic_output(wmi_class, sp.check_output(f"wmic {wmi_class} get {' '.join(properties)}", shell=True).decode())