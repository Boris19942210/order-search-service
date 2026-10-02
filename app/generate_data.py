import random
import sys
import time
from datetime import datetime, timedelta
from .database import init_db, get_connection

FIRST = ["Иван", "Пётр", "Сергей", "Анна", "Мария", "Ольга", "Дмитрий", "Елена"]
LAST = ["Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов", "Попов"]
STATUSES = ["pending", "processing", "delivered", "cancelled"]


def generate(n: int = 5_000_000, batch: int = 50_000) -> None:
    init_db()
    conn = get_connection()
    cur = conn.cursor()
    start = time.time()

    base_date = datetime(2023, 1, 1)

    for offset in range(0, n, batch):
        rows = []
        for i in range(offset + 1, min(offset + batch, n) + 1):
            name = f"{random.choice(FIRST)} {random.choice(LAST)}"
            created = base_date + timedelta(
                days=random.randint(0, 1000),
                seconds=random.randint(0, 86400),
            )
            rows.append((
                i,
                f"ORD-{i:010d}",
                name,
                created.strftime("%Y-%m-%d %H:%M:%S"),
                random.choice(STATUSES),
                round(random.uniform(100, 100000), 2),
            ))
        cur.executemany(
            "INSERT INTO orders (id, order_number, client_name, "
            "created_at, status, amount) VALUES (?, ?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()
        print(f"Inserted {min(offset + batch, n)} / {n}")

    conn.close()
    print(f"Done in {time.time() - start:.1f}s")


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 5_000_000
    generate(count)