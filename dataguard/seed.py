from .warehouse import reset_database, revenue_summary


def main():
    reset_database()
    print("Seeded synthetic raw_orders table.")
    print(revenue_summary())


if __name__ == "__main__":
    main()
