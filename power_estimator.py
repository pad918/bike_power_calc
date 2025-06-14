import argparse
import sys
from gps_data.gpx_loader import GPXLoader


def main():
    sys.argv.append("Drevviken1.gpx")
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("filename")
    args = arg_parser.parse_args()
    
    # Load gps data
    points = GPXLoader(args.filename).load()
    print(points)


if __name__ == "__main__":
    main()