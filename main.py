import sys
from crawl import get_html

def main():
    if len(sys.argv) <2:
        print("no website provided")
        sys.exit(1)
    elif len(sys.argv) >2:
        print("too many arguments provided")
        sys.exit(1)
    else:
        print(f"starting crawl of: {sys.argv[1]}")
    response = get_html(sys.argv[1])
    print(response)

if __name__ == "__main__":
    main()
