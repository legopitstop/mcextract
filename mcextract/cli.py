from argparse import ArgumentParser

from mcextract import __version__, MCExtractAPI
     
parser = ArgumentParser()
parser.add_argument(
    "-V",
    "--version",
    action="store_true",
    help="print the mcextract version number and exit.",
)

# Parser
modules = parser.add_subparsers(dest="module")

# extract <fp> --assets --data
extract_parser = modules.add_parser("extract", help='Extract data or assets folders from the Minecraft jar.')
extract_parser.add_argument(dest="jar_file", type=str)
extract_parser.add_argument("--assets", "-assets", action="store_true")
extract_parser.add_argument("--data", "-data", action="store_true")
extract_parser.add_argument("--output", "-o", type=str, const=None)
extract_parser.add_argument("--acceptEULA", "-eula", action="store_true", default=False)

# map <fp> <objects>
map_parser = modules.add_parser("map", help='Maps Minecraft\'s objects using an index file.')  
map_parser.add_argument(dest="index_file", type=str)
map_parser.add_argument(dest="objects_directory", nargs='?', type=str, const=None)
map_parser.add_argument("--output", "-o", type=str, const=None)
map_parser.add_argument("--acceptEULA", "-eula", action="store_true", default=False)

# generate <version> --assets --data --reports
generate_parser = modules.add_parser("generate", help='Use Minecraft\'s built-in data generator.')
generate_parser.add_argument(dest="mcversion", type=str)
generate_parser.add_argument("--output", "-o", type=str, const=None)
generate_parser.add_argument("--acceptEULA", "-eula", action="store_true", default=False)

def main():
    args, unknownargs = parser.parse_known_args()
    api = MCExtractAPI()
    if args.version:
        print(__version__)
        return

    try:
        match args.module:
            case 'generate':
                api.generate(args.mcversion, unknownargs, args.output, args.acceptEULA)                
            case 'extract': 
                api.extract(args.jar_file, args.assets, args.data, args.output, args.acceptEULA)
            case 'map':
                api.map(args.index_file, args.objects_directory, args.output, args.acceptEULA)
    except Exception as err:
        api.logger.exception(err)

if __name__ == '__main__':
    main()