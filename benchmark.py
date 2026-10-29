import argparse
import time

from db import generate_users


def main():
    parser = argparse.ArgumentParser(
        description="Measure faker.generate_users throughput."
    )
    parser.add_argument("--users", type=int, default=10000)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument(
        "--locale",
        choices=["en_US", "de_DE"],
        default="en_US",
    )
    parser.add_argument("--seed", default="benchmark-v1")
    parser.add_argument("--warmup", type=int, default=1)
    args = parser.parse_args()

    if args.users < 1 or not 1 <= args.batch_size <= 1000:
        parser.error("users must be positive; batch size must be 1–1000")

    if args.warmup > 0:
        generate_users(args.locale, args.seed, 0, min(10, args.batch_size))

    generated = 0
    batch_index = 0
    start = time.perf_counter()
    while generated < args.users:
        size = min(args.batch_size, args.users - generated)
        rows = generate_users(
            args.locale, args.seed, batch_index, size
        )
        generated += len(rows)
        batch_index += 1
    elapsed = time.perf_counter() - start
    rate = generated / elapsed if elapsed else 0.0

    print(f"Locale: {args.locale}")
    print(f"Seed: {args.seed}")
    print(f"Users generated: {generated}")
    print(f"Batch size: {args.batch_size}")
    print(f"Elapsed seconds: {elapsed:.3f}")
    print(f"Users per second: {rate:.1f}")


if __name__ == "__main__":
    main()
