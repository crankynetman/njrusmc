#!/usr/bin/env python

"""
File:    check_cache_headers.py
Author:  Nicholas Russo (http://njrusmc.net)
Purpose: Quickly check to ensure the HTTP cache testing files all have the
         expected Cache-Control headers. These should not be overwritten
         during new CI pushes, but this script guarantees it.
"""

import sys
import requests


def main():
    """
    Execution begins here.
    """

    # After enabling CloudFront TLS, avoid HTTP redirection, use direct links.
    # Using http://njrusmc.net (no "S") will cause header stripping unless
    # redirects are followed, which is unnecessary to validate.
    url_dict = {
        "http": "http://njrusmc.net.s3-website.us-east-1.amazonaws.com",
        "https": "https://njrusmc.net",
    }

    # Enumerate the files and the expected Cache-Control header string
    file_dict = {
        "zero128k_none.test": None,
        "zero128k_public.test": "public",
        "zero128k_public60.test": "public, max-age=60",
        "zero128k_public3600.test": "public, max-age=3600",
        "zero128k_private.test": "private",
        "zero128k_private60.test": "private, max-age=60",
        "zero128k_private3600.test": "private, max-age=3600",
        "zero128k_nocache.test": "no-cache",
        "zero128k_nocache60.test": "no-cache, max-age=60",
        "zero128k_nocache3600.test": "no-cache, max-age=3600",
        "zero128k_nostore.test": "no-store",
        "rand128k_none.test": None,
        "rand128k_public.test": "public",
        "rand128k_public60.test": "public, max-age=60",
        "rand128k_public3600.test": "public, max-age=3600",
        "rand128k_private.test": "private",
        "rand128k_private60.test": "private, max-age=60",
        "rand128k_private3600.test": "private, max-age=3600",
        "rand128k_nocache.test": "no-cache",
        "rand128k_nocache60.test": "no-cache, max-age=60",
        "rand128k_nocache3600.test": "no-cache, max-age=3600",
        "rand128k_nostore.test": "no-store",
    }

    # Create a long lived session and iterate over dict items
    sess = requests.session()
    failures = 0
    for mode, url in url_dict.items():
        print(f"\nTesting access protocol {mode.upper()}")
        for filename, cc_header in file_dict.items():
            # Reveal test case and issue HEAD request
            target = f"{url}/cache/{filename}"
            print(f"Testing {target} for {cc_header} ... ", end="")
            resp = sess.head(target)

            # If a Cache-Control header was specified, test for equality
            if cc_header:
                if resp.headers["Cache-Control"] == cc_header:
                    print("OK!")
                else:
                    print("FAIL!")
                    failures += 1

            # Else a Cache-Control header was not specified, ensure absence
            else:
                if "Cache-Control" not in resp.headers:
                    print("OK!")
                else:
                    print("FAIL!")
                    failures += 1

    # Exit with rc equal to failure count (0 means success)
    sys.exit(failures)


if __name__ == "__main__":
    main()
