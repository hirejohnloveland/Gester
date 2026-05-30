from gester.infrastructure.storage.sqlite.sqlite_db import initialize_database


def main() -> None:
    print("Starting Gester")
    initialize_database()


if __name__ == "__main__":
    main()
