
import psycopg

from syncforge.database import get_database_url


def main():
    connection = psycopg.connect(get_database_url())

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT current_database(), version();"
            )

            result = cursor.fetchone()

            print("Database:", result[0])
            print(
                "PostgreSQL version:",
                result[1].split(",")[0],
            )
            print("Connection successful!")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
