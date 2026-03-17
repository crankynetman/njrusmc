#!/usr/bin/env python

"""
File:    check_links.py
Author:  Nicholas Russo (http://njrusmc.net)
Purpose: Second-stage CI check to ensure links to both HTTP-accessible
         websites and local files embedded with HTML documents are resolvable.
         It also checks that images are resolvable, of the proper format, and
         less than a certain threshold size.
"""

import os
import sys
import time
import imghdr
import requests
from requests.exceptions import ReadTimeout
from bs4 import BeautifulSoup

# requests doesn't specify a default timeout; define some values
TIMEOUT = 20
ATTEMPTS = 5
WAIT_SEC = 5


def get_soup(uri):
    """
    Given a URI of an html file (eg, ../index.html) or a hyperlink
    (eg, http://njrusmc.net), grab the HTML text and parse it into
    a beautifulsoup4 object and return it.

    Raises ValueError if the input file does not begin with 'http' or
    end with '.html'.
    """
    print(f"\nRead URI    '{uri}'")

    # If the input is a website, perform an HTTP GET. Else, it's a file.
    if uri.lower().startswith("http"):
        # Note that there are no header options here as it is assumed the
        # website being tested (ie, my own) will not require custom headers.
        get_resp = requests.get(uri, timeout=TIMEOUT)
        html_text = get_resp.text
    elif uri.lower().endswith(".html"):
        # Simply open the file and read the text using standard methods.
        with open(uri, "r", encoding="utf-8") as handle:
            html_text = handle.read()
    else:
        # If neither of the above are true, the input is invalid
        raise ValueError("input URI was not an HTTP link nor an HTML file")

    # Perform the parsing and store in a beautifulsoup object to be returned
    soup = BeautifulSoup(html_text, "html.parser")
    return soup


def test_links(links, path):
    """
    Given a list of links (URIs of HTML files or hyperlinks) and a directory
    base path for file lookups, validate the health of each link. For
    hyperlinks, perform a simple HTTP GET, optionally supplying a user-agent
    if the link contains type 'ua'. For files, ensure the file exists. These
    checks ensure that the links presented to viewers via HTML are valid
    links that will, at a minimum, result in a loaded webpage or a downloaded
    file.

    Raises HTTPError if the HTTP GET operation fails.
    Raises ValueError if the HTML file does not exist.
    """
    for link in links:
        # Store some temporary variables to simplify future code.
        # Navigation anchors won't have href, but should have name.
        href = link.get("href", link.get("name", "UNKNOWN LINK"))
        link_type = link.get("type")

        # Some links aren't hyperlinks or files, such as a 'mailto' link.
        # These can safely be skipped when the type of "skip" is seen.
        # Likewise, we should skip the navigation anchors.
        if link_type == "skip":
            print(f"  Skip link  '{href[:70]}'")
            continue

        # If the link is a hyperlink, perform an HTTP HEAD. Else, it's a file.
        if href.lower().startswith("http"):
            print(f"  HTTP HEAD  '{href[:67]}' ... ", end="")

            # Determine if a user-agent header is needed, when type is "ua".
            # Ternary operation not used here in case there are future choices.
            headers = {"Accept-Encoding": "deflate, gzip;q=1.0, *;q=0.5"}
            if link_type == "ua":
                ua_str = (
                    "Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Firefox/41.0"
                )
                headers.update({"User-Agent": ua_str})

            # Don't need to GET the entire message body, just the HEAD element
            # is sufficient. Also, check for status less than 400 (no error)
            try:
                head_resp = requests.head(
                    href, headers=headers, timeout=TIMEOUT, allow_redirects=True
                )
            except ReadTimeout:
                head_resp = None

            # HTTP GET failed, which happens sometimes on some sites. Try
            # a full HTTP GET in case the server struggles with HEAD requests
            if not head_resp or not head_resp.ok:
                print("FAIL!")

                # Attempt to issue a GET request multiple times
                success = False
                for i in range(ATTEMPTS):
                    print(f"  HTTP GET {i+1} '{href[:67]}' ... ", end="")
                    get_resp = requests.get(
                        href, headers=headers, timeout=TIMEOUT
                    )

                    # Request succeeded; stop retrying
                    if get_resp.ok:
                        success = True
                        break

                    # Request failed; wait for a while
                    print("FAIL!")
                    time.sleep(WAIT_SEC)

                if not success:
                    # All requests failed; raise HTTPError
                    get_resp.raise_for_status()
        else:
            # Assemble filename and test to see if file exists.
            filename = path + href
            print(f"  Is file?   '{filename[:68]}' ... ", end="")
            if not os.path.isfile(filename):
                raise ValueError(f"'{filename}' is not a file")

        print("OK!")


def test_imgs(imgs, path):
    """
    Like the test_links() function above, this validates that the image files
    are less than a maximum size (currently 512) and are of a specific subset
    of valid image types (currently jpeg, png, or gif). The list of images
    is a list of links with 'src' defined and the path is the directory base
    path for looking up the image files.

    Raises FileNotFoundError if the image file does not exist.
    Raises ValueError if the file is too large.
    Raises TypeError if the file is not a valid image type.
    """
    max_image_size = 1000000  # 1 MB
    valid_img = ["jpeg", "png", "gif"]

    for img in imgs:
        # Store some temporary variables to simplify future code.
        src = img.get("src")
        filename = path + src

        # Test to see if the image is a valid file.
        print(f"  Is image?  '{filename[:68]}' ... ", end="")
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"'{filename}' is not an file")

        # Test to see if the image is less than the maximum allowed size.
        img_size = os.path.getsize(filename)
        if img_size > max_image_size:
            raise ValueError(f"'{filename}' too big: {img_size}B")

        # Test to see if the image is in one of the acceptable image formats.
        img_type = imghdr.what(filename)
        if not img_type or not img_type in valid_img:
            raise TypeError(f"Image ;{filename}' is invalid")

        print("OK!")


def main(argv):
    """
    Execution begin here based on CLI arguments. A single CLI argument is
    required, which is the URI to check. Typically this is a website
    (eg, http://njrusmc.net) or an HTML file (eg, ../index.html).
    """
    if len(argv) != 2:
        print("usage: python check_links.py '<uri>'")
        sys.exit(1)

    # Print the CLI argument back for logging purposes.
    uri = sys.argv[1]
    print(f"CLI input   '{uri}'")

    # Determine the directory path one level up from where this script is.
    # That is where the index.html file should be, and all the sub directories.
    dirpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + "/"
    if not os.path.isdir(dirpath):
        print(f"{dirpath} is not a directory")

    # Parse the user input URI and grab all the links. The front page does
    # not have any images which reduces loading time.
    links = get_soup(uri).find_all("a")

    print(f"Found {len(links)} total links in {uri}")
    for link in links:
        # Ignore some top-level links if marked as skip
        if link.get("type") == "skip":
            continue

        # Store some temporary variables to improve readability. Note that
        # the soup object is only created once and is referenced multiple
        # times below (for links and images).
        href = link.get("href")
        soup = get_soup(dirpath + href)
        subdirpath = f"{dirpath}{os.path.dirname(href)}/"

        # Scan the HTML data from each subpath and check the link validity.
        sublinks = soup.find_all("a")
        test_links(sublinks, subdirpath)

        # Scan the HTML data from each subpath and check the image validity.
        images = soup.find_all("img")
        test_imgs(images, subdirpath)

    # Positive confirmation that program succeed
    print("ALL LINKS ARE HEALTHY")


# Execute the main() function only when this file is called directly.
if __name__ == "__main__":
    main(sys.argv)
