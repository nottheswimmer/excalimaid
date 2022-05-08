import json
import math
import re
import time
from dataclasses import dataclass, field
from random import randrange
from typing import Optional, List, Any, Dict
from enum import Enum
from uuid import uuid4

import bs4
from bs4 import BeautifulSoup


def random_id() -> str:
    return uuid4().hex[:16]

@dataclass
class Excalidraw:
    elements: List['Element'] = field(default_factory=list)
    app_state: 'AppState' = field(default_factory=lambda: AppState())
    files: Dict[str, 'File'] = field(default_factory=dict)
    source: str = 'https://nottheswimmer.org'
    version: int = 2
    type: str = 'excalidraw'

    def to_json(self):
        return {
            "type": self.type,
            "version": self.version,
            "source": self.source,
            "elements": [e.to_json() for e in self.elements],
            "appState": self.app_state.to_json(),
            "files": {k: v.to_json() for k, v in self.files.items()},
        }

    @classmethod
    def from_json(cls, json: Dict[str, Any]):
        return cls(
            type=json["type"],
            version=json.get("version", 2),
            source=json.get("source", "https://excalidraw.com"),
            elements=[Element.from_json(e) for e in json["elements"]],
            app_state=AppState.from_json(json["appState"]) if json.get("appState") else AppState(),
            files={k: File.from_json(v) for k, v in json["files"].items()},
        )

    @classmethod
    def from_svg(cls, svg: str):
        tree = BeautifulSoup(svg, "html.parser")

        return cls.from_svg_tree(tree)

    @classmethod
    def from_svg_tree(cls, tree: BeautifulSoup):
        return cls(elements=Element.from_svg_tree(tree))


@dataclass
class AppState:
    view_background_color: str = '#ffffff'
    grid_size: Optional[int] = None

    def to_json(self):
        return {
            "viewBackgroundColor": self.view_background_color,
            "gridSize": self.grid_size,
        }

    @classmethod
    def from_json(cls, json: Dict[str, Any]):
        return cls(
            view_background_color=json["viewBackgroundColor"],
            grid_size=json["gridSize"],
        )


class TypeEnum(Enum):
    ARROW = "arrow"
    DIAMOND = "diamond"
    ELLIPSE = "ellipse"
    FREEDRAW = "freedraw"
    IMAGE = "image"
    LINE = "line"
    RECTANGLE = "rectangle"
    TEXT = "text"


@dataclass
class BoundElement:
    id: str
    type: TypeEnum

    def to_json(self):
        return {
            "id": self.id,
            "type": self.type.value,
        }

    @classmethod
    def from_json(cls, be):
        return cls(
            id=be["id"],
            type=TypeEnum(be["type"]),
        )


class Arrowhead(Enum):
    DOT = "dot"
    ARROW = "arrow"
    BAR = "bar"
    TRIANGLE = "triangle"


@dataclass
class Binding:
    element_id: str
    focus: float
    gap: float

    def to_json(self):
        return {
            "elementId": self.element_id,
            "focus": self.focus,
            "gap": self.gap,
        }

    @classmethod
    def from_json(cls, json: Dict[str, Any]):
        return cls(
            element_id=json["elementId"],
            focus=json["focus"],
            gap=json["gap"],
        )


class Style(Enum):
    CROSS_HATCH = "cross-hatch"
    HACHURE = "hachure"
    SOLID = "solid"


class StrokeStyle(Enum):
    SOLID = "solid"
    DASHED = "dashed"
    DOTTED = "dotted"


class StrokeSharpness(Enum):
    ROUND = "round"
    SHARP = "sharp"


class TextAlign(Enum):
    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"


class VerticalAlign(Enum):
    BOTTOM = "bottom"
    MIDDLE = "middle"
    TOP = "top"


@dataclass
class Element:
    type: TypeEnum
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0
    id: str = field(default_factory=random_id)
    fill_style: Style = Style.HACHURE
    stroke_width: int = 1
    stroke_style: StrokeStyle = StrokeStyle.SOLID
    roughness: int = 0
    opacity: int = 100
    stroke_sharpness: StrokeSharpness = StrokeSharpness.SHARP
    seed: int = field(default_factory=lambda: randrange(0, 2**31))
    version: int = 1
    version_nonce: int = field(default_factory=lambda: randrange(0, 2**31))
    is_deleted: bool = False
    updated: int = field(default_factory=lambda: int(time.time() * 1000))
    angle: int = 0
    background_color: str = "transparent"
    stroke_color: str = "#000000"
    group_ids: List[str] = field(default_factory=list)
    bound_elements: Optional[List[BoundElement]] = None
    link: Optional[str] = None
    points: Optional[List[List[float]]] = None
    last_committed_point: Optional[List[float]] = None
    start_binding: Optional[Binding] = None
    end_binding: Optional[Binding] = None
    start_arrowhead: Optional[Arrowhead] = None
    end_arrowhead: Optional[Arrowhead] = None
    text: Optional[str] = None
    font_size: Optional[int] = None
    font_family: Optional[int] = None
    text_align: Optional[TextAlign] = None
    vertical_align: Optional[VerticalAlign] = None
    baseline: Optional[int] = None
    container_id: Optional[str] = None
    original_text: Optional[str] = None
    pressures: Optional[List[float]] = None
    simulate_pressure: Optional[bool] = None
    status: Optional[str] = None
    file_id: Optional[str] = None
    scale: Optional[List[float]] = None

    def to_json(self):
        obj = {
            "id": self.id,
            "type": self.type.value,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "angle": self.angle,
            "fillStyle": self.fill_style.value,
            "strokeWidth": self.stroke_width,
            "strokeStyle": self.stroke_style.value,
            "roughness": self.roughness,
            "opacity": self.opacity,
            "groupIds": self.group_ids,
            "strokeSharpness": self.stroke_sharpness.value,
            "seed": self.seed,
            "version": self.version,
            "versionNonce": self.version_nonce,
            "isDeleted": self.is_deleted,
            "updated": self.updated,
            "backgroundColor": self.background_color,
            "strokeColor": self.stroke_color,
        }
        if self.bound_elements:
            obj["boundElements"] = [be.to_json() for be in self.bound_elements]
        if self.link:
            obj["link"] = self.link
        if self.points:
            obj["points"] = self.points
        if self.last_committed_point:
            obj["lastCommittedPoint"] = self.last_committed_point
        if self.start_binding:
            obj["startBinding"] = self.start_binding.to_json()
        if self.end_binding:
            obj["endBinding"] = self.end_binding.to_json()
        if self.start_arrowhead:
            obj["startArrowhead"] = self.start_arrowhead.value
        if self.end_arrowhead:
            obj["endArrowhead"] = self.end_arrowhead.value
        if self.text:
            obj["text"] = self.text
        if self.font_size:
            obj["fontSize"] = self.font_size
        if self.font_family:
            obj["fontFamily"] = self.font_family
        if self.text_align:
            obj["textAlign"] = self.text_align.value
        if self.vertical_align:
            obj["verticalAlign"] = self.vertical_align.value
        if self.baseline:
            obj["baseline"] = self.baseline
        if self.container_id:
            obj["containerId"] = self.container_id
        if self.original_text:
            obj["originalText"] = self.original_text
        if self.pressures:
            obj["pressures"] = self.pressures
        if self.simulate_pressure:
            obj["simulatePressure"] = self.simulate_pressure
        if self.status:
            obj["status"] = self.status
        if self.file_id:
            obj["fileId"] = self.file_id
        if self.scale:
            obj["scale"] = self.scale
        return obj

    @classmethod
    def from_json(cls, json_obj: Dict[str, Any]):
        obj = cls(
            id=json_obj["id"],
            type=TypeEnum(json_obj["type"]),
            x=json_obj["x"],
            y=json_obj["y"],
            width=json_obj["width"],
            height=json_obj["height"],
            angle=json_obj["angle"],
            fill_style=Style(json_obj["fillStyle"]),
            stroke_width=json_obj["strokeWidth"],
            stroke_style=StrokeStyle(json_obj["strokeStyle"]),
            roughness=json_obj["roughness"],
            opacity=json_obj["opacity"],
            group_ids=json_obj["groupIds"],
            stroke_sharpness=StrokeSharpness(json_obj["strokeSharpness"]),
            seed=json_obj["seed"],
            version=json_obj["version"],
            version_nonce=json_obj["versionNonce"],
            is_deleted=json_obj["isDeleted"],
            updated=json_obj["updated"],
            background_color=json_obj["backgroundColor"],
            stroke_color=json_obj["strokeColor"],
        )
        if json_obj.get("boundElements") is not None:
            obj.bound_elements = [
                BoundElement.from_json(be) for be in json_obj["boundElements"]
            ]
        if json_obj.get("link") is not None:
            obj.link = json_obj["link"]
        if json_obj.get("points") is not None:
            obj.points = json_obj["points"]
        if json_obj.get("lastCommittedPoint") is not None:
            obj.last_committed_point = json_obj["lastCommittedPoint"]
        if json_obj.get("startBinding") is not None:
            obj.start_binding = Binding.from_json(json_obj["startBinding"])
        if json_obj.get("endBinding") is not None:
            obj.end_binding = Binding.from_json(json_obj["endBinding"])
        if json_obj.get("startArrowhead") is not None:
            obj.start_arrowhead = Arrowhead(json_obj["startArrowhead"])
        if json_obj.get("endArrowhead") is not None:
            obj.end_arrowhead = Arrowhead(json_obj["endArrowhead"])
        if json_obj.get("text") is not None:
            obj.text = json_obj["text"]
        if json_obj.get("fontSize") is not None:
            obj.font_size = json_obj["fontSize"]
        if json_obj.get("fontFamily") is not None:
            obj.font_family = json_obj["fontFamily"]
        if json_obj.get("textAlign") is not None:
            obj.text_align = TextAlign(json_obj["textAlign"])
        if json_obj.get("verticalAlign") is not None:
            obj.vertical_align = VerticalAlign(json_obj["verticalAlign"])
        if json_obj.get("baseline") is not None:
            obj.baseline = json_obj["baseline"]
        if json_obj.get("containerId") is not None:
            obj.container_id = json_obj["containerId"]
        if json_obj.get("originalText") is not None:
            obj.original_text = json_obj["originalText"]
        if json_obj.get("pressures") is not None:
            obj.pressures = json_obj["pressures"]
        if json_obj.get("simulatePressure") is not None:
            obj.simulate_pressure = json_obj["simulatePressure"]
        if json_obj.get("status") is not None:
            obj.status = json_obj["status"]
        if json_obj.get("fileId") is not None:
            obj.file_id = json_obj["fileId"]
        if json_obj.get("scale") is not None:
            obj.scale = json_obj["scale"]
        return obj

    @classmethod
    def from_svg_edge_path(cls, edge_path: bs4.element.Tag) -> list["Element"]:
        self = cls(TypeEnum.ARROW)

        # Get the ID from the ID attribute
        self.id = edge_path["id"]

        # Get the opacity from the style
        self.opacity = float(edge_path["style"].split("opacity:")[1].split(";")[0]) * 100 if "opacity" in edge_path["style"] else 100

        # The element looks like this:
        # <g class="edgePath LS-A LE-B" id="L-A-B" style="opacity: 1;"><path class="path" d="M37.4375,85.60759244689221L41.604166666666664,83.79799370574351C45.770833333333336,81.9883949645948,54.104166666666664,78.36919748229741,62.4375,78.37778055933052C70.77083333333333,78.38636363636364,79.10416666666667,82.02272727272727,83.27083333333333,83.84090909090908L87.4375,85.6590909090909" marker-end="url(#arrowhead48)" style="fill:none"></path><defs><marker id="arrowhead48" markerheight="6" markerunits="strokeWidth" markerwidth="8" orient="auto" refx="9" refy="5" viewbox="0 0 10 10"><path class="arrowheadPath" d="M 0 0 L 10 5 L 0 10 z" style="stroke-width: 1; stroke-dasharray: 1, 0;"></path></marker></defs></g>

        # Get the path from the path attribute
        path = edge_path.find("path")

        # Get the other points
        d = path["d"].replace(",", " ").split()

        # Get the stroke width if it exists
        try:
            stroke_width = float(path["style"].split("stroke-width:")[1].split(";")[0].removesuffix("px")) if "stroke-width" in path["style"] else 1
        except Exception as e:
            print(f"Error parsing stroke width: {e}")
            stroke_width = 1

        if stroke_width > 1:
            self.stroke_width = 4

        def pop_x_y():
            x, y = d.pop(0), d.pop(0)
            assert x[0].isalpha()
            if len(x) == 1:
                x = y
                y = d.pop(0)
            else:
                x = x[1:]
            for c in "LC":
                if c in y:
                    y, put_back = y.split(c, 1)
                    d.insert(0, c + put_back)
                    break
            return float(x), float(y)

        def pop_x1_y1_x2_y2_x_y():
            x1, y1, x2, y2, x, y = d.pop(0), d.pop(0), d.pop(0), d.pop(0), d.pop(0), d.pop(0)
            assert x1[0].isalpha()
            if len(x1) == 1:
                x1 = y1
                y1 = x2
                x2 = y2
                y2 = x
                x = d.pop(0)
            else:
                x1 = x1[1:]
            for c in "LC":
                if c in y:
                    y, put_back = y.split(c, 1)
                    d.insert(0, c + put_back)
                    break
            return float(x1), float(y1), float(x2), float(y2), float(x), float(y)

        cur_x, cur_y = pop_x_y()

        self.x = cur_x
        self.y = cur_y

        self.points = [[0.0, 0.0]]

        def _bezier_curve_point(point_list, t, x_or_y):
            if len(point_list) == 1:
                return point_list[0][x_or_y]
            return round(
                _bezier_curve_point(point_list[:-1], t, x_or_y) * (1 - t) + _bezier_curve_point(point_list[1:], t,
                                                                                                x_or_y) * t, 5)

        def bezier_curve_recursive(def_points, speed=0.1):
            points = []
            for t in [_ * speed for _ in range(int((1 + speed * 2) // speed))]:
                points.append([_bezier_curve_point(def_points, t, 0), _bezier_curve_point(def_points, t, 1)])
            return points

        while d:
            if d[0][0] == "L":
                next_x, next_y = pop_x_y()
                self.points.append([next_x-self.x, next_y-self.y])
                cur_x, cur_y = next_x, next_y
            elif d[0][0] == "C":
                x1, y1, x2, y2, next_x, next_y = pop_x1_y1_x2_y2_x_y()
                curve = [[x1-self.x, y1-self.y],
                         [x2-self.x, y2-self.y],
                         [next_x-self.x, next_y-self.y]]

                curve = bezier_curve_recursive(curve, 0.1)
                # if len(curve) > 10:
                #     curve = curve[:-2]

                self.points.extend(curve)

                cur_x, cur_y = next_x, next_y
            elif d[0][0] in "zZ":
                """
                Close the current subpath by connecting the last point of the path with its initial point. 
                If the two points are at different coordinates, a straight line is drawn between those two points.
                """
                self.points.append([0.0, 0.0])
                break
            else:
                raise Exception("Unknown path command: " + d[0])


        # a, b, c = path["d"].split("L")
        # start_x, start_y = a[1:].split(",")
        # end_x, end_y = c.split(",")
        # xys = []
        # xys.append(end_x)
        # xys.append(end_y)
        #
        # self.x = float(start_x)
        # self.y = float(start_y)
        # self.points = [[0., 0.]]
        #
        # for x, y in zip(xys[0::2], xys[1::2]):
        #     if "C" in x:
        #         x = x.split("C")[1]
        #     if "C" in y:
        #         y = y.split("C")[1]
        #     x = float(x)
        #     y = float(y)
        #     x -= self.x
        #     y -= self.y
        #     self.points.append([x, y])

        self.width = max(x for x, y in self.points) - min(x for x, y in self.points)
        self.height = max(y for x, y in self.points) - min(y for x, y in self.points)

        # Check for marker-start
        if path.get("marker-start"):
            self.start_arrowhead = Arrowhead.TRIANGLE
        if path.get("marker-end") or not self.start_arrowhead:
            self.end_arrowhead = Arrowhead.TRIANGLE

        return [self]

    @classmethod
    def from_svg_edge_label(cls, edge_label: bs4.element.Tag) -> list["Element"]:
        # Get edgeLabel span
        span = edge_label.find("span")
        if span.get("id"):
            edge_label.id = span["id"]
        nodes = cls.from_svg_node(edge_label)
        for node in nodes:
            if node.type == TypeEnum.TEXT:
                node.font_size *= 0.8
            else:
                node.background_color = "#e0e0e0"
        return nodes

    @classmethod
    def from_svg_node(cls, node: bs4.element.Tag) -> list["Element"]:

        # <g class="node default" id="flowchart-A-17" style="opacity: 1;"
        # transform="translate(22.71875,92)"><rect class="label-container"
        # height="39" rx="0" ry="0" width="29.4375" x="-14.71875" y="-19.5"></rect>
        # <g class="label" transform="translate(0,0)"><g transform="translate(-4.71875,-9.5)">
        # <foreignobject height="19" width="9.4375">
        # <div style="display: inline-block; white-space: nowrap;"
        # xmlns="http://www.w3.org/1999/xhtml">A</div></foreignobject></g></g></g>

        try:
            tsfm_x = float(node["transform"].split("translate(")[1].split(",")[0])
            tsfm_y = float(node["transform"].split("translate(")[1].split(",")[1][:-1])
        except Exception as e:
            tsfm_x = tsfm_y = 0.0

        # If the node has the "root" class, do a recursive search for nodes
        if node.get("class") and "root" in node["class"]:
            return cls.from_svg_tree(node, tsfm_x=tsfm_x, tsfm_y=tsfm_y, tree_id=random_id())

        objs = []
        txt_objs = []


        print("NODE:", node)

        for fo in node.find_all("foreignobject"):

            if not fo.text:
                print(f"Skip empty foreignobject: {fo}")
                continue

            txt = cls(TypeEnum.TEXT)
            txt.x = tsfm_x
            txt.y = tsfm_y
            txt.width = float(fo["width"])
            txt.height = float(fo["height"])

            sub_tsfm = fo.get("transform")
            if sub_tsfm:
                txt.x += float(sub_tsfm.split("translate(")[1].split(",")[0])
                txt.y += float(sub_tsfm.split("translate(")[1].split(",")[1][:-1])
            else:
                txt.x -= txt.width / 2
            txt.y -= txt.height / 2
            txt.text = fo.text
            txt.original_text = txt.text

            txt.font_size = 16
            txt.font_family = 2
            txt.text_align = TextAlign.CENTER
            txt.vertical_align = VerticalAlign.MIDDLE
            txt.baseline = txt.height - (txt.height - txt.font_size) / 2
            txt.id = fo.get("id", txt.id)
            objs.append(txt)
            txt_objs.append(txt)


        line_objs = []
        for line in node.find_all("line"):
            ln = cls.from_svg_line(line)[0]
            ln.y += tsfm_y
            ln.x += tsfm_x
            ln.bound_elements = []
            for txt in txt_objs:
                txt.container_id = ln.id
                ln.bound_elements.append(BoundElement(txt.id, txt.type))
            objs.append(ln)
            line_objs.append(ln)


        joiner_objs = line_objs
        if len(txt_objs) == 1:
            joiner_objs += txt_objs

        rectangle = node.find("rect")
        if rectangle:
            rect = cls.from_svg_rectangle(rectangle)[0]
            rect.y += tsfm_y
            rect.x += tsfm_x
            rect.x -= rect.width / 2
            rect.y -= rect.height / 2
            rect.bound_elements = []
            for txt in joiner_objs:
                txt.container_id = rect.id
                rect.bound_elements.append(BoundElement(txt.id, txt.type))
            objs.append(rect)

        polygon = node.find("polygon")
        if polygon:
            poly = cls.from_svg_polygon(polygon)[0]
            poly.y += tsfm_y
            poly.x += tsfm_x
            poly.x -= poly.width / 2
            poly.bound_elements = []
            for txt in joiner_objs:
                txt.container_id = poly.id
                poly.bound_elements.append(BoundElement(txt.id, txt.type))
            objs.append(poly)

        circle = node.find("circle")
        if circle:
            circ = cls.from_svg_circle(circle)[0]
            circ.y += tsfm_y
            circ.x += tsfm_x
            circ.y -= circ.height / 4
            circ.bound_elements = []
            for txt in joiner_objs:
                txt.container_id = circ.id
                circ.bound_elements.append(BoundElement(txt.id, txt.type))
            objs.append(circ)

        group_id = random_id()
        for obj in objs:
            obj.group_ids = [group_id]

        print("->", objs)

        return objs

    @classmethod
    def from_svg_rectangle(cls, rectangle: bs4.element.Tag, include_xy=False) -> list["Element"]:
        # <rect height="19" rx="0" ry="0" width="58.203125"></rect>
        self: 'Element' = cls(TypeEnum.RECTANGLE)
        self.height = float(rectangle["height"])
        self.width = float(rectangle["width"])
        if include_xy:
            if rectangle.get("x", "0") != "0":
                self.x = float(rectangle["x"])
            if rectangle.get("y", "0") != "0":
                self.y = float(rectangle["y"])
        if (rectangle.get("rx") and rectangle.get("rx") != "0") or (rectangle.get("ry") and rectangle.get("ry") != "0"):
            self.stroke_sharpness = StrokeSharpness.ROUND
        return [self]

    @classmethod
    def from_svg_polygon(cls, polygon: bs4.element.Tag) -> list["Element"]:
        # <polygon class="label-container" transform="translate(-69.88050041198731,69.88050041198731)" points="69.88050041198731,0 139.76100082397463,-69.88050041198731 69.88050041198731,-139.76100082397463 0,-69.88050041198731"></polygon>
        self = cls(TypeEnum.DIAMOND)
        self.x = float(polygon["transform"].split("translate(")[1].split(",")[0])
        self.y = float(polygon["transform"].split("translate(")[1].split(",")[1][:-1])
        pairs = polygon["points"].split(" ")
        points = []
        for pair in pairs:
            x, y = pair.split(",")
            points.append((float(x), float(y)))
        width = max(points, key=lambda p: p[0])[0] - min(points, key=lambda p: p[0])[0]
        height = max(points, key=lambda p: p[1])[1] - min(points, key=lambda p: p[1])[1]
        self.width = width
        self.height = height
        self.x += width / 2
        self.y -= height
        # self.x -= 13
        # self.y += 15
        return [self]

    @classmethod
    def from_svg_circle(cls, circle: bs4.element.Tag) -> list["Element"]:
        # <circle class="label-container" r="33.765625" x="-33.765625" y="-19.5"></circle>
        self = cls(TypeEnum.ELLIPSE)
        self.x = float(circle.get("x", "0"))
        self.y = float(circle.get("y", "0"))
        self.width = self.height = float(circle["r"]) * 2
        # self.x += 10
        return [self]

    @classmethod
    def from_svg_line(cls, line: bs4.element.Tag) -> list["Element"]:
        # <line class="divider" x1="-59.5859375" x2="59.5859375" y1="-44" y2="-44"></line>
        self = cls(TypeEnum.LINE)
        self.x = float(line["x1"])
        self.y = float(line["y1"])
        self.width = abs(float(line["x2"]) - self.x)
        self.height = abs(float(line["y2"]) - self.y)
        self.points = [[0, 0], [float(line["x2"]) - self.x, float(line["y2"]) - self.y]]
        return [self]

    @classmethod
    def from_svg_tree(cls, tree: BeautifulSoup | bs4.element.Tag, tsfm_x=0., tsfm_y=0., tree_id=None) -> list["Element"]:
        if tree_id is None:
            tree_id = random_id()

        elements = []

        # For every "path" element that is a child of edgePaths, create a fake <g> element and do the same
        edgePaths = tree.find('g', class_='edgePaths')
        if edgePaths:
            for i, path in enumerate(edgePaths.find_all('path', recursive=False)):
                g = bs4.element.Tag(name='g')
                g['class'] = 'edgePath'
                g.append(path)
                g['id'] = f'root-edgepath-{i}'
                g['style'] = path['style']
                elements += Element.from_svg_edge_path(g)
            for edge_path in edgePaths.find_all('g', class_='edgePath', recursive=False):
                elements += Element.from_svg_edge_path(edge_path)

        edgeLabels = tree.find('g', class_='edgeLabels')
        if edgeLabels:
            for edge_label in edgeLabels.find_all('g', class_='edgeLabel', recursive=False):
                elements += Element.from_svg_edge_label(edge_label)

        nodes = tree.find('g', class_='nodes')
        if nodes:
            for node in nodes.find_all('g', class_='node', recursive=False):
                elements += Element.from_svg_node(node)
            for root in nodes.find_all('g', class_='root', recursive=False):
                elements += Element.from_svg_node(root)
            a = nodes.find_all('a', recursive=False)
            for a in a:
                transform = a.get('transform')
                a_tsfm_x = a_tsfm_y = 0
                if transform:
                    m = re.search(r'translate\(([-\d.]+),\s*([-\d.]+)', transform)
                    if m:
                        a_tsfm_x = float(m.group(1))
                        a_tsfm_y = float(m.group(2))
                link_elements = []
                for node in a.find_all('g', class_='node', recursive=False):
                    link_elements += Element.from_svg_node(node)
                for root in a.find_all('g', class_='root', recursive=False):
                    link_elements += Element.from_svg_node(root)
                for link_element in link_elements:
                    link_element.link = a.get('xlink:href')
                    link_element.x += a_tsfm_x
                    link_element.y += a_tsfm_y
                elements += link_elements


        clusters = tree.find('g', class_='clusters')
        if clusters:
            for cluster in clusters.find_all('g', class_='cluster', recursive=False):
                rect = cluster.find('rect')
                rect_elts = Element.from_svg_rectangle(rect, include_xy=True)
                rect_x = rect_y = 0
                for rect_elt in rect_elts:
                    rect_x = rect_elt.x
                    rect_y = rect_elt.y
                    rect_elt.x = rect_elt.y = 0
                g = cluster.find('g')
                g_elts = Element.from_svg_node(g)
                for g_elt in g_elts:
                    g_elt.x -= rect_x
                    g_elt.y -= rect_y
                elements += rect_elts + g_elts

                # for g_elt in g_elts:
                #     g_elt.x += g_elt.width / 2


                group_id = g.get('id', random_id())
                for elt in g_elts + rect_elts:
                    if not elt.group_ids:
                        elt.group_ids = [group_id]
                    else:
                        elt.group_ids.append(group_id)

                print("RECT_ELTS", rect_elts)

        for element in elements:
            element.x += tsfm_x
            element.y += tsfm_y

            if tree_id:
                if element.group_ids:
                    element.group_ids.append(tree_id)
                else:
                    element.group_ids = [tree_id]

        return elements


@dataclass
class File:
    mime_type: str
    id: str
    data_url: str
    created: int

    def to_json(self):
        return {
            "mimeType": self.mime_type,
            "id": self.id,
            "dataURL": self.data_url,
            "created": self.created,
        }

    @staticmethod
    def from_json(json_obj):
        return File(
            mime_type=json_obj["mimeType"],
            id=json_obj["id"],
            data_url=json_obj["dataURL"],
            created=json_obj["created"],
        )


if __name__ == '__main__':
    with open(r"C:\Users\windo\Pictures\example7.excalidraw", "r") as f:
        data = f.read()
    json_obj = json.loads(data)
    excalidraw = Excalidraw.from_json(json_obj)
    with open(r"C:\Users\windo\Pictures\example7-2.excalidraw", "w") as f:
        f.write(json.dumps(excalidraw.to_json()))
    print(excalidraw.to_json())
