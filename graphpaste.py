import json
import time

import pyperclip
from pynput import keyboard

import excalidraw
import mermaid


def get_clipboard_text():
    return pyperclip.paste()


def get_clipboard_as_graph():
    text = get_clipboard_text()

    if not isinstance(text, str):
        print(f"Clipboard is not a string: {text}")
        return None

    if "excalidraw/clipboard" in text:
        try:
            parsed = json.loads(text)
            excali = excalidraw.Excalidraw.from_json(parsed)
            text = excali.elements[0].original_text
        except Exception as e:
            print("Error parsing clipboard:", e)
    else:
        return ""

    if not text:
        return ""
    text = text.strip()

    if "graph:" in text:
        print(f"Warning: You seem to have accidentally added a colon to the graph. Removing it....")
        text = text.replace("graph:", "graph")

    if " -> " in text:
        print(f"Warning: You seem to have accidentally added a -> to the graph. Replacing with -->")
        text = text.replace(" -> ", " --> ")

    if " - " in text:
        print(f"Warning: You seem to have accidentally added a - to the graph. Replacing with --")
        text = text.replace(" - ", " -- ")

    if not text:
        print("Clipboard is empty")
        return None

    return text

    # first_line = text.splitlines()[0]
    # for graph_type in "graph", "sequenceDiagram", "gantt", "classDiagram", "gitGraph", "erDiagram", "journey":
    #     if graph_type in first_line:
    #         return text
    #
    # out = ["graph"]
    # for line in text.split("\n"):
    #     if line.startswith("#"):
    #         continue
    #     out.append(f"  {line}")
    # return "\n".join(out)

    # if "graph" in text.splitlines()[0]:
    #     return text
    # lines = ["graph"]
    # for line in text.split("\n"):
    #     lines.append("  " + line)
    # return "\n".join(lines)


def copy_to_clipboard(text):
    pyperclip.copy(text)


def convert_clipboard():
    text = get_clipboard_as_graph()
    mermaid_svg = mermaid.mermaid_to_svg(text)
    print(mermaid_svg)
    if not mermaid_svg:
        print("No mermaid diagram found in clipboard", text)
        return False
    excali = excalidraw.Excalidraw.from_svg(mermaid_svg)
    excali_json = excali.to_json()
    if not excali_json["elements"]:
        print("No elements found in clipboard", text)
        return False
    copy_to_clipboard(json.dumps(excali_json))
    print("Copied to clipboard:", excali_json)
    return True


CONTROL_KEYS = {keyboard.Key.ctrl, keyboard.Key.ctrl_l}

current = set()


def on_press(key):
    if key in CONTROL_KEYS:
        current.add(key)

    if current.issubset(CONTROL_KEYS) and repr(key).lower() in ["c", r"'\x03'"]:
        time.sleep(0.05)
        try:
            convert_clipboard()
        except Exception as e:
            import traceback
            traceback.print_exc()


def on_release(key):
    current.discard(key)


def main():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


if __name__ == "__main__":
    main()
