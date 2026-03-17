#!/usr/bin/env python

"""
File:    check_redirects.py
Author:  Nicholas Russo (http://njrusmc.net)
Purpose: Quickly check to ensure the HTTP redirect files are working
         correctly. This reads in the contents from the files locally,
         performs a HEAD request to ensure the "Location" response header
         matches the redirect URL contained in each file.
"""

import os
import sys
import requests


def main(directory):
    """
    Execution begins here.
    """

    # Define base URL for all redirect files by appending the directory.
    # If HTTP is used, a second redirect is necessary, complicating the logic.
    # base_url = f"http://njrusmc.net/{directory}"
    base_url = f"https://njrusmc.net/{directory}"

    # Create a long lived session and iterate over all redirect files
    failures = 0
    sess = requests.session()
    for filename in os.listdir(directory):

        # Open each file to collect the URL inside
        filepath = f"{directory}{filename}"
        with open(filepath, "r", encoding="utf-8") as handle:
            redirect_url = handle.read().strip()

        # Print a message displaying the current item and issue HEAD request
        print(f"Testing {filepath} to {redirect_url} ... ", end="")
        resp = sess.head(f"{base_url}{filename}", allow_redirects=False)

        # Response should be a redirect (status code 300-399)
        if resp.is_redirect:

            # Ensure the Location URL matches the redirect URL from file
            location = resp.headers.get("Location")
            if location == redirect_url:
                print("OK!")

            # Response was a redirect but contents are incorrect/missing
            else:
                print("FAIL: URL mismatch")
                print(f"  Location: {location}")
                print(f"  redirect_url: {redirect_url}")
                failures += 1

        # Response was not a redirect; display actual status code
        else:
            print(f"FAIL: not a redirect - {resp.status_code}")
            failures += 1

    # Exit with rc equal to failure count (0 means success)
    sys.exit(failures)


if __name__ == "__main__":
    main("r/")
