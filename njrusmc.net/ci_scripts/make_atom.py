#!/usr/bin/env python

"""
File:    make_atom.py
Author:  Nicholas Russo (http://njrusmc.net)
Purpose: CD process to build the atom.xml artifact which allows users to
         subscribe to the blog. The script finds all HTML blog files and
	     extracts the relevant information needed by Atom.
"""

import os
from datetime import datetime
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader


def get_blog_files(years):
    """
    Walk the filesystem for a given directory, grabbing only the HTML
    files from a specified list of years. Return a list of strings in
    'path/blog' format for future iteration, which will open up each file to
    perform parsing.
    """
    blog_files = []

    # For every year selected, recursively get all HTML files
    for year in years:
        for path, dirs, files in os.walk(top=f"blog/{year}"):
            if not dirs:
                blog_files.extend(
                    [f"{path}/{blog}" for blog in files if "html" in blog]
                )

    # List has been assembled; return the result
    return blog_files


def main():
    """
    Execution begins here. Contains the core logic of the script. Blog posts
    are parsed using BS4 and assembled into a list of dictionaries so they can
    be templated into XML for use with Atom/RSS readers. Here is an example of
    the JSON structure for a given blog post in the list:

    {
      "title": "Automating Networks with Python",
      "updated": "2019-06-07",
      "url": "http://njrusmc.net/blog/2019/hide/ps-py-net.html",
      "summary": "\nAnnouncement: My Automating Networks with Python course
        has\njust published on Pluralsight! For a link to the training
        content, please visit my
        \n<a href=\"../../../course/course.html\">courses page</a>.\n",
      "categories": [
        "training",
        "pluralsight"
      ]
    }
    """

    # Create main data dictionary with an initial timestamp of a date
    # in the past, so any new updates will certainly overwrite it.
    # Instantiate an empty list of blogs (strings) for future extension.
    data = {"feed_updated": "2019-01-01", "blogs": []}

    # Iterate over the number of blogs found
    blog_files = get_blog_files([2019, 2021, 2023, 2024])
    for blog_file in sorted(blog_files, reverse=True):

        # Open the file, read the text, and parse HTML data using BS4.
        print(f"{blog_file} ... ", end="")
        with open(blog_file, "r", encoding="utf-8") as stream:
            html_text = stream.read()
        soup = BeautifulSoup(html_text, "html.parser")

        # If the "active" tag is absent, the blog should not be added to the Atom feed.
        # Else the "active" tag is present, so keep processing.
        active_tag = soup.find("meta", attrs={"name": "active"})
        if active_tag is None:
            print("inactive")
            continue

        # Split the date from the title, then convert the date to the proper Atom
        # format of YYYY-MM-DD from the blog format of DD Mmm YYYY.
        date_title_tag = soup.find("title")
        date_title_elems = date_title_tag.text.split(" - ")
        date_ymd = datetime.strptime(date_title_elems[0], "%d %b %Y").strftime(
            "%Y-%m-%d"
        )

        # If the current date is newer than the previous feed date, update
        # the overall feed date. This results in the newest blog governing
        # the feed update value.
        if date_ymd > data["feed_updated"]:
            data["feed_updated"] = date_ymd

        # Find category string. If it exists, split on comma, otherwise
        # use an empty list to gracefully kill the jinja2 for loop
        category_tags = soup.find("meta", attrs={"name": "category"})
        if category_tags:
            category_strs = category_tags.get("content").split(",")
        else:
            category_strs = []

        # The summary should be the second element in the list
        body_elems = soup.find("body").findChildren(recursive=False)

        # Convert the bs4.element.Tag object into a string, but
        # retain the HTML formatting
        summary_str = body_elems[1].decode_contents()

        # Assemble temporary dict to add to overall blog list
        blog_dict = {
            "title": date_title_elems[1],
            "updated": date_ymd,
            "url": "http://njrusmc.net/" + blog_file,
            "summary": summary_str,
            "categories": category_strs,
        }
        data["blogs"].append(blog_dict)
        print("OK!")

    # Useful debugging to print final blog dict in JSON format
    # import json; print(json.dumps(data["blogs"], indent=2))

    # Use jinja2 to build the proper Atom XML file for the blog
    j2_env = Environment(
        loader=FileSystemLoader("."), trim_blocks=True, autoescape=True
    )
    template = j2_env.get_template("ci_scripts/atom_xml.j2")
    with open("blog/atom.xml", "w", encoding="utf-8") as atom_xml:
        atom_xml.write(template.render(data=data))

    print("XML data written to blog/atom.xml")


if __name__ == "__main__":
    main()
