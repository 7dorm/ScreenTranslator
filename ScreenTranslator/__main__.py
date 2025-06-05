from ScreenTranslator import start_server, runScreenTranslator
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(prog="ScreenTranslator", description="ScreenTranslator CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Запустить перевод")
    run_parser.add_argument("filePath", help="Путь к файлу")
    run_parser.add_argument("destinationPath", nargs="?", default=None, help="Путь назначения (опционально)")

    server_parser = subparsers.add_parser("server", help="Запустить сервер")

    args = parser.parse_args()

    if args.command == "run":
        runScreenTranslator(
            filePath=args.filePath,
            destinationPath=args.destinationPath,
            request=None
        )
    elif args.command == "server":
        start_server()

if __name__ == "__main__":
    main()
