import argparse
import sys
from .service import METHODS, SCOPES, list_areas, run_analysis


def menu(prompt, options):
    for code, label in options.items():
        print(f"  {code:>4}  {label}")
    while True:
        choice = input(prompt + ": ").strip().casefold()
        matches = [k for k, label in options.items() if choice in (k.casefold(), label.casefold())]
        if len(matches) == 1:
            return matches[0]
        print("Digite um código da lista.")


def main():
    parser = argparse.ArgumentParser(description="Interligações entre metas dos ODS")
    parser.add_argument("--versao", choices=METHODS)
    parser.add_argument("--tipo", choices=SCOPES)
    parser.add_argument("--area", help="Código M49 no IGES/JRC ou código do catálogo SDGIndex.")
    parser.add_argument("--metodo", choices=["pearson", "spearman", "ambos"])
    parser.add_argument("--csv", help="Coleta UNSD já salva, para IGES/JRC.")
    parser.add_argument("--saida", help="Pasta que conterá IGES_JRC e SDGIndex.")
    args = parser.parse_args()
    version = args.versao or METHODS[int(menu("Escolha a versão", {"1": "IGES/JRC", "2": "SDGIndex"})) - 1]
    scope = args.tipo or SCOPES[int(menu("Escolha o recorte", {"1": "Região", "2": "País"})) - 1]
    area = args.area or menu("Escolha a área", list_areas(version, scope))
    result = run_analysis(version, scope, area, method=args.metodo, csv_path=args.csv, output_dir=args.saida)
    print(f"Resultado completo: {result}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("Execução cancelada.")
    except Exception as exc:
        sys.exit(f"Erro: {exc}")
