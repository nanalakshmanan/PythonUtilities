import argparse
import json
import orjson


def pretty_to_orjson(input_file: str, output_file: str):
    """Converts indented JSON to compact orjson format."""
    try:
        with open(input_file, 'r', encoding='utf-8') as fin:
            data = json.load(fin)

        with open(output_file, 'wb') as fout:
            fout.write(b'{\n  "hashes": [\n')
            hashes = data.get("hashes", [])
            for i, entry in enumerate(hashes):
                if i > 0:
                    fout.write(b',\n')
                fout.write(orjson.dumps(entry))
            fout.write(b'\n  ]\n}\n')

        print(f"Converted pretty JSON to compact orjson: {output_file}")
    except Exception as e:
        print(f"Error in pretty_to_orjson: {e}")


def orjson_to_pretty(input_file: str, output_file: str, indent: int = 4):
    """Converts compact orjson file to pretty-printed indented JSON."""
    try:
        with open(input_file, 'rb') as fin:
            raw = fin.read()
            parsed = json.loads(raw)

        with open(output_file, 'w', encoding='utf-8') as fout:
            json.dump(parsed, fout, indent=indent, ensure_ascii=False)

        print(f"Converted compact orjson to pretty JSON: {output_file}")
    except Exception as e:
        print(f"Error in orjson_to_pretty: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert between pretty-printed JSON and compact orjson formats."
    )
    parser.add_argument(
        '--input', '-i', required=True, help="Input JSON file"
    )
    parser.add_argument(
        '--output', '-o', required=True, help="Output JSON file"
    )
    parser.add_argument(
        '--to-compact', action='store_true',
        help="Convert from pretty JSON to compact orjson format"
    )
    parser.add_argument(
        '--to-pretty', action='store_true',
        help="Convert from compact orjson to pretty-printed JSON"
    )
    parser.add_argument(
        '--indent', type=int, default=4,
        help="Indentation level for pretty-printed JSON (default: 4)"
    )

    args = parser.parse_args()

    if args.to_compact == args.to_pretty:
        print("Error: Specify either --to-compact or --to-pretty (but not both)")
        return

    if args.to_compact:
        pretty_to_orjson(args.input, args.output)
    else:
        orjson_to_pretty(args.input, args.output, args.indent)


if __name__ == "__main__":
    main()
