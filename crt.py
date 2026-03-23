import argparse
import sys
import time

import requests


class CrtShClient:
    def __init__(
        self,
        domain: str,
        timeout: int = 15,
        retries: int = 3,
        retry_backoff: float = 1.0,
    ):
        self.domain = domain.lower().strip()
        self.timeout = timeout
        self.retries = retries
        self.retry_backoff = retry_backoff
        self.url = f"https://crt.sh/?q=%25.{self.domain}&output=json"
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) "
                "Gecko/20100101 Firefox/60.0"
            )
        }
        self.found_urls = set()

    def _fetch_rows_with_retry(self):
        total_attempts = self.retries + 1

        for attempt in range(1, total_attempts + 1):
            try:
                response = requests.get(
                    self.url,
                    headers=self.headers,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                return response.json()
            except requests.Timeout:
                if attempt >= total_attempts:
                    raise

                sleep_seconds = self.retry_backoff * (2 ** (attempt - 1))
                print(
                    (
                        f"[i] Timeout contacting crt.sh "
                        f"(attempt {attempt}/{total_attempts}). "
                        f"Retrying in {sleep_seconds:.1f}s..."
                    ),
                    file=sys.stderr,
                )
                time.sleep(sleep_seconds)

    def subdomain_scrape(self):
        rows = self._fetch_rows_with_retry()

        for row in rows:
            name_value = row.get("name_value", "")
            if not name_value:
                continue

            # crt.sh may return multiple names separated by new lines.
            for candidate in name_value.splitlines():
                host = candidate.strip().lower().replace("*.", "")
                if host and (host == self.domain or host.endswith(f".{self.domain}")):
                    self.found_urls.add(host)

    def run(self):
        self.subdomain_scrape()

    def get_subdomains(self):
        return sorted(self.found_urls)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Find subdomains for a domain using public certificate transparency logs (crt.sh)."
    )
    parser.add_argument(
        "-d",
        "--domain",
        required=True,
        help="Target domain, for example: example.com",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=15,
        help="HTTP timeout in seconds (default: 15)",
    )
    parser.add_argument(
        "-r",
        "--retries",
        type=int,
        default=3,
        help="Number of retries after timeout (default: 3)",
    )
    parser.add_argument(
        "--retry-backoff",
        type=float,
        default=1.0,
        help="Initial retry backoff in seconds for timeouts (default: 1.0)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    client = CrtShClient(
        args.domain,
        timeout=args.timeout,
        retries=args.retries,
        retry_backoff=args.retry_backoff,
    )

    try:
        client.run()
    except requests.RequestException as exc:
        print(f"[!] Network error while querying crt.sh: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"[!] Failed to parse crt.sh response: {exc}", file=sys.stderr)
        return 1

    for subdomain in client.get_subdomains():
        print(subdomain)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

