import sys
import math
import urllib.request
import urllib.parse
import json

BASE_URL = "https://ubounty.app/api/bounties"
DEFAULT_LIMIT = 20
DEFAULT_PAGE_SIZE = 10


class BrowseCommand:
    def __init__(self, args):
        self.language = args.language
        self.min_amount = args.min_amount
        self.max_amount = args.max_amount
        self.difficulty = args.difficulty
        self.limit = args.limit
        self.page_size = args.page_size

    def _build_url(self, offset=0):
        params = {}
        if self.language:
            params["language"] = self.language
        if self.min_amount is not None:
            params["min_amount"] = str(self.min_amount)
        if self.max_amount is not None:
            params["max_amount"] = str(self.max_amount)
        if self.difficulty:
            params["difficulty"] = self.difficulty
        params["limit"] = str(self.limit)
        params["offset"] = str(offset)
        query = urllib.parse.urlencode(params)
        return "{}?{}".format(BASE_URL, query) if query else BASE_URL

    def _fetch(self, offset=0):
        url = self._build_url(offset)
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = resp.read().decode("utf-8")
                return json.loads(data)
        except urllib.error.HTTPError as e:
            print("Error: API returned HTTP {}".format(e.code), file=sys.stderr)
            sys.exit(1)
        except urllib.error.URLError as e:
            print("Error: Could not reach API — {}".format(e.reason), file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError:
            print("Error: Unexpected response from API.", file=sys.stderr)
            sys.exit(1)

    def _print_header(self):
        print(
            "{:<6}  {:<45}  {:>10}  {:<20}  {:<10}".format(
                "#", "Title", "Amount", "Repo", "Difficulty"
            )
        )
        print("-" * 98)

    def _print_row(self, idx, bounty):
        title = str(bounty.get("title", "")).strip()
        title = title[:42] + "..." if len(title) > 45 else title

        amount_raw = bounty.get("amount", "")
        currency = bounty.get("currency", "USDC")
        amount = "{} {}".format(amount_raw, currency) if amount_raw != "" else "N/A"

        repo = str(bounty.get("repo", bounty.get("repository", ""))).strip()
        repo = repo[:17] + "..." if len(repo) > 20 else repo

        difficulty = str(bounty.get("difficulty", "")).strip() or "—"

        print(
            "{:<6}  {:<45}  {:>10}  {:<20}  {:<10}".format(
                idx, title, amount, repo, difficulty
            )
        )

    def _print_summary(self, total_shown, total_available):
        print()
        if total_available is not None:
            print(
                "Showing {} of {} bounty(ies).".format(total_shown, total_available)
            )
        else:
            print("Showing {} bounty(ies).".format(total_shown))

    def run(self):
        offset = 0
        shown = 0
        page_num = 1
        total_available = None
        first_page = True

        while True:
            payload = self._fetch(offset)

            # Support both list responses and dict responses with a 'results' key
            if isinstance(payload, list):
                bounties = payload
            elif isinstance(payload, dict):
                bounties = payload.get("results", payload.get("bounties", []))
                total_available = payload.get("total", payload.get("count", None))
            else:
                print("Error: Unexpected data format from API.", file=sys.stderr)
                sys.exit(1)

            if not bounties:
                if first_page:
                    print("No bounties found matching your criteria.")
                break

            page_bounties = bounties[: self.page_size]

            if first_page:
                self._print_header()
                first_page = False
            else:
                print()

            for bounty in page_bounties:
                shown += 1
                self._print_row(shown, bounty)

            offset += len(page_bounties)
            remaining_limit = self.limit - shown

            if remaining_limit <= 0 or len(page_bounties) < self.page_size:
                self._print_summary(shown, total_available)
                break

            # Prompt for next page
            try:
                answer = input(
                    "\n-- Page {} | {} shown so far. Press Enter for next page, or 'q' to quit: ".format(
                        page_num, shown
                    )
                ).strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if answer == "q":
                self._print_summary(shown, total_available)
                break

            page_num += 1


def register_parser(subparsers):
    parser = subparsers.add_parser(
        "browse",
        help="Discover open bounties from the terminal.",
        description=(
            "Browse available bounties. Filter by language, amount, or difficulty. "
            "Results are paginated for readability."
        ),
    )
    parser.add_argument(
        "--language",
        metavar="LANG",
        default=None,
        help="Filter by programming language (e.g. python, javascript).",
    )
    parser.add_argument(
        "--min-amount",
        "--min",
        dest="min_amount",
        metavar="AMOUNT",
        type=float,
        default=None,
        help="Minimum bounty amount (in USDC).",
    )
    parser.add_argument(
        "--max-amount",
        "--max",
        dest="max_amount",
        metavar="AMOUNT",
        type=float,
        default=None,
        help="Maximum bounty amount (in USDC).",
    )
    parser.add_argument(
        "--difficulty",
        metavar="LEVEL",
        default=None,
        choices=["easy", "medium", "hard"],
        help="Filter by difficulty: easy, medium, or hard.",
    )
    parser.add_argument(
        "--limit",
        metavar="N",
        type=int,
        default=DEFAULT_LIMIT,
        help="Maximum number of bounties to fetch (default: {}).".format(DEFAULT_LIMIT),
    )
    parser.add_argument(
        "--page-size",
        metavar="N",
        type=int,
        default=DEFAULT_PAGE_SIZE,
        dest="page_size",
        help="Number of results shown per page (default: {}).".format(DEFAULT_PAGE_SIZE),
    )
    parser.set_defaults(func=lambda args: BrowseCommand(args).run())
    return parser