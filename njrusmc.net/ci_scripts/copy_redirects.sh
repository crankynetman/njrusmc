#!/bin/bash
# File:    copy_redirects.sh
# Version: Bash 3.2.57(1)
# Author:  Nicholas Russo (http://njrusmc.net)
# Purpose: Finds all files in the r/ directory which represent
#          redirection objects. The file contents will contain the
#          redirection target, whether it's another object or a URL.
#          Then, the "aws cp" command is used to perform the upload
#          to the S3 bucket using the correct metadata.
#
# Find all files in the /r directory, excluding any directories
for f in $(find ./r -type f); do
  # Print the filename followed by the URL read from the file
  echo -n "checking $f - "
  redirect_url=$(<$f)
  # Print the filename and URL for logging
  echo $redirect_url
  # Upload the file and set the website redirect to the redirect URL
  aws s3 cp $f s3://njrusmc.net/r/ --website-redirect $redirect_url
done
