import base64
import json

import requests
from bs4 import BeautifulSoup

import excalidraw

def mermaid_to_svg(graph: str) -> str:
    graph_bytes = graph.encode("ascii")
    base64_bytes = base64.b64encode(graph_bytes)
    base64_string = base64_bytes.decode("ascii")
    uri = "https://mermaid.ink/svg/" + base64_string

    e = None
    for timeout in range(2, 9, 2):
        try:
            result = requests.get(uri, timeout=timeout)
            break
        except requests.exceptions.Timeout as e:
            continue
    else:
        if e:
            raise e
        else:
            raise Exception("Cosmic rays")

    if result.text == "invalid encoded code":
        return ""
    return result.text


def svg_to_excalidraw(svg: str) -> str:
    root = excalidraw.Excalidraw.from_svg(svg)
    return root.to_json()



if __name__ == "__main__":
    graph = """
    graph
        U1(User 1) -- Message --> W1[Webserver 1]
        W1 -- Message --> Q[Queue]
        Q -- Message --> W2[Webserver 2]
        W2 -- Message --> U2[User 2]
        U2 -- Establish WebRTC --> U1
        W2 -- Confirmation --> W1
    """

    graph = """
    graph TD
        A[Christmas] -->|Get money| B(Go shopping)
        B --> C{Let me think}
        C -->|One| D(Laptop)
        C -->|Two| E((iPhone))
        C -->|Three| F[fa:fa-car Car]
    """

#     graph = """
# graph TD
#  U[User] --> |Sup| S{Server}
#  S --> |Not much, you?| U
# """

#     graph = """\
# classDiagram
#     Animal <|-- Duck
#     Animal <|-- Fish
#     Animal <|-- Zebra
#     Animal : +int age
#     Animal : +String gender
#     Animal: +isMammal()
#     Animal: +mate()
#     class Duck{
#       +String beakColor
#       +swim()
#       +quack()
#     }
#     class Fish{
#       -int sizeInFeet
#       -canEat()
#     }
#     class Zebra{
#       +bool is_wild
#       +run()
#     }
# """

#     graph = """\
# stateDiagram-v2
#     [*] --> Still
#     Still --> [*]
#     Still --> Moving
#     Moving --> Still
#     Moving --> Crash
#     Crash --> [*]
# """

#     graph = """\
# gantt
#     title A Gantt Diagram
#     dateFormat  YYYY-MM-DD
#     section Section
#     A task           :a1, 2014-01-01, 30d
#     Another task     :after a1  , 20d
#     section Another
#     Task in sec      :2014-01-12  , 12d
#     another task      : 24d
# """

#     graph = """\
# pie title Pets adopted by volunteers
#     "Dogs" : 386
#     "Cats" : 85
#     "Rats" : 15
# """

    # graph = """
    # graph LR;
    #     A--> B & C & D;
    #     B--> A & E;
    #     C--> A & E;
    #     D--> A & E;
    #     E--> B & C & D;
    # """

    graph = """
flowchart TB
    c1-->a2
    subgraph one
    a1-->a2
    end
    subgraph two
    b1-->b2
    end
    subgraph three
    c1-->c2
    end
"""

    svg = mermaid_to_svg(graph)
    tree = BeautifulSoup(svg, "html.parser")
    with open("example_svg.svg", "w") as f:
        f.write(tree.prettify())
    print("SVG:")
    print(tree.prettify())
    print("\nDEBUG:")
    excali = svg_to_excalidraw(svg)
    raw = json.dumps(excali, indent=2)
    with open("example_excalidraw.excalidraw", "w") as f:
        f.write(raw)
    with open("example_excalidraw.clipboard", "w") as f:
        f.write(raw)
    print("\nOUTPUT:")
    print(raw)
