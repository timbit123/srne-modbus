#!/usr/bin/env python3
"""Generate a filtered Lovelace dashboard that removes entities whose registers
are in the skip state (unsupported or persistently out-of-range on this firmware).

Usage:
    python3 generate_dashboard.py [--output lovelace-dashboard-current.yaml]

Reads:
    register_skip_state.json  — written by modbus.py at runtime
    lovelace-dashboard.yaml   — the full template dashboard
    mqtt_topic_config.py      — to map register addresses to entity IDs
    .env                      — for MQTT_TOPIC (device slug)

Writes:
    lovelace-dashboard-current.yaml  (or --output path)
"""

import json
import os
import re
import sys
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available — parse .env manually
    try:
        with open(".env") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _, _v = _line.partition("=")
                    _v = _v.split("#")[0].strip().strip('"').strip("'")
                    os.environ.setdefault(_k.strip(), _v)
    except FileNotFoundError:
        pass


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower().strip()).strip("_")


def load_skip_state(path: str) -> set[int]:
    try:
        with open(path) as f:
            data = json.load(f)
        return {int(k, 16) for k in data.keys()}
    except FileNotFoundError:
        return set()
    except Exception as e:
        print(f"Warning: could not load skip state from {path}: {e}", file=sys.stderr)
        return set()


def build_excluded_entity_ids(skipped_regs: set[int], mqtt_topic: str) -> set[str]:
    """Parse mqtt_topic_config.py statically to find entity IDs whose register
    is in the skip set."""
    device_slug = re.sub(r"[^a-z0-9]+", "_", mqtt_topic.lower()).strip("_")
    excluded = set()

    try:
        with open("mqtt_topic_config.py") as f:
            content = f.read()
    except FileNotFoundError:
        print("Warning: mqtt_topic_config.py not found", file=sys.stderr)
        return excluded

    config_start = content.find("mqtt_config: dict")
    if config_start == -1:
        return excluded
    section = content[config_start:]

    current_key = None
    current_type = "sensor"
    current_name = None
    current_register = None

    def flush():
        nonlocal current_key, current_type, current_name, current_register
        if current_key and current_name and current_register is not None:
            if current_register in skipped_regs:
                entity_id = f"{current_type}.{device_slug}_{slugify(current_name)}"
                excluded.add(entity_id)
        current_key = None
        current_type = "sensor"
        current_name = None
        current_register = None

    for line in section.split("\n"):
        km = re.match(r'\s{4}"([^"]+)":\s*\{', line)
        if km:
            flush()
            current_key = km.group(1)

        if current_key:
            tm = re.search(r'"topic_type":\s*"([^"]+)"', line)
            if tm:
                current_type = tm.group(1)
            nm = re.search(r'"name":\s*"([^"]+)"', line)
            if nm and current_name is None:
                current_name = nm.group(1)
            rm = re.search(r'"register":\s*(0x[0-9A-Fa-f]+|\d+)', line)
            if rm and current_register is None:
                raw = rm.group(1)
                current_register = int(raw, 16) if raw.startswith("0x") else int(raw)

    flush()
    return excluded


def filter_dashboard(template_path: str, excluded_ids: set[str]) -> str:
    """Remove entity entries from the dashboard YAML whose entity ID is excluded.
    Handles the common patterns:
      - entity: <id>
        name: ...
      - entity: <id>   (no name line)
    """
    with open(template_path) as f:
        lines = f.readlines()

    output = []
    skip_next_name = False
    removed = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this is an entity line
        em = re.match(r"(\s+)- entity:\s*(\S+)", line)
        if em:
            entity_id = em.group(2)
            if entity_id in excluded_ids:
                # Skip this entity line
                removed += 1
                i += 1
                # Also skip the immediately following 'name:' line if present
                if i < len(lines) and re.match(r"\s+name:\s*", lines[i]):
                    i += 1
                continue
        output.append(line)
        i += 1

    print(f"Removed {removed} excluded entities from dashboard", file=sys.stderr)
    return remove_empty_cards("".join(output))


def remove_empty_cards(yaml_text: str) -> str:
    """Remove cards and folds that have no entity list items left after filtering.
    Only removes cards that use an 'entities:' list — gauge, power-flow, and
    conditional cards that use a single 'entity:' key are left untouched."""
    lines = yaml_text.split("\n")

    # Cards start at 6-space indent: "      - type:" inside a view's cards list
    card_start_re = re.compile(r"^      - ")

    # Find card block boundaries
    card_starts = [i for i, ln in enumerate(lines) if card_start_re.match(ln)]
    card_starts.append(len(lines))  # sentinel

    blocks_to_remove: list[tuple[int, int]] = []
    removed_cards = 0

    for j in range(len(card_starts) - 1):
        start = card_starts[j]
        end = card_starts[j + 1]
        block = lines[start:end]

        # Only consider cards that use an entities: list (not gauge/power-flow)
        has_entities_key = any(re.match(r"\s+entities:\s*$", ln) for ln in block)
        if not has_entities_key:
            continue

        # Check whether any list entity items remain
        has_entity_item = any(re.match(r"\s+- entity:\s+\S", ln) for ln in block)
        if has_entity_item:
            continue

        # Card is empty — also capture a preceding comment line if present
        actual_start = start
        if start > 0 and re.match(r"\s+#", lines[start - 1]):
            actual_start = start - 1

        blocks_to_remove.append((actual_start, end))
        removed_cards += 1

    # Remove from bottom to top so indices stay valid
    result = list(lines)
    for start, end in reversed(blocks_to_remove):
        del result[start:end]

    print(f"Removed {removed_cards} empty cards from dashboard", file=sys.stderr)
    return "\n".join(result)


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--output",
        default="lovelace-dashboard-current.yaml",
        help="Output file path (default: lovelace-dashboard-current.yaml)",
    )
    parser.add_argument(
        "--mqtt-topic",
        default=None,
        help="MQTT topic prefix (overrides MQTT_TOPIC in .env)",
    )
    parser.add_argument(
        "--skip-state",
        default=os.getenv("MODBUS_SKIP_STATE_FILE", "register_skip_state.json"),
        help="Path to register skip state JSON",
    )
    parser.add_argument(
        "--template",
        default="lovelace-dashboard.yaml",
        help="Template dashboard YAML",
    )
    args = parser.parse_args()

    mqtt_topic = args.mqtt_topic or os.getenv("MQTT_TOPIC") or "srne1"
    print(f"Using MQTT_TOPIC: {mqtt_topic}", file=sys.stderr)

    skipped = load_skip_state(args.skip_state)
    print(f"Skipped registers: {len(skipped)}", file=sys.stderr)

    excluded = build_excluded_entity_ids(skipped, mqtt_topic)
    print(f"Excluded entity IDs: {len(excluded)}", file=sys.stderr)
    for e in sorted(excluded):
        print(f"  {e}", file=sys.stderr)

    filtered = filter_dashboard(args.template, excluded)

    with open(args.output, "w") as f:
        f.write(filtered)

    print(f"Written to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
