import argparse
import sys
from .service import METHODS, SCOPES, list_areas, run_analysis


def menu(prompt, options):
    for code, label in options.items():
        print(f"  {code:>4}  {label}")
    while True:
        choice = input(prompt + ': ').strip().casefold()
        matches = [k for k, label in options.items() if choice in (k.casefold(), label.casefold())]
        if len(matches) == 1:
            return matches[0]
        print('Enter a code from the list.')


def main():
    parser = argparse.ArgumentParser(description='Interlinkages among SDG targets')
    parser.add_argument('--version', '--versao', choices=METHODS)
    parser.add_argument('--scope', '--tipo', type=lambda v: {'regiao': 'region', 'pais': 'country'}.get(v, v), choices=SCOPES)
    parser.add_argument('--area', help='M49 code for IGES/JRC or SDGIndex catalog code.')
    parser.add_argument('--method', '--metodo', type=lambda v: 'both' if v == 'ambos' else v, choices=['pearson', 'spearman', 'both'])
    parser.add_argument('--csv', help='Previously saved UNSD collection for IGES/JRC.')
    parser.add_argument('--output', '--saida', help='Folder containing IGES_JRC and SDGIndex outputs.')
    args = parser.parse_args()
    version = args.version or METHODS[int(menu('Choose the version', {'1': 'IGES/JRC', '2': 'SDGIndex'})) - 1]
    scope = args.scope or SCOPES[int(menu('Choose the scope', {'1': 'Region', '2': 'Country'})) - 1]
    area = args.area or menu('Choose the area', list_areas(version, scope))
    result = run_analysis(version, scope, area, method=args.method, csv_path=args.csv, output_dir=args.output)
    print(f"Complete results: {result}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit('Execution cancelled.')
    except Exception as exc:
        sys.exit(f"Error: {exc}")
