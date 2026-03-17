#!/bin/bash
# File:    html_lint.sh
# Version: Bash 3.2.57(1)
# Author:  Nicholas Russo (http://njrusmc.net)
# Purpose: First-stage CI check to ensure HTML is free from defect
#          or common styling errors. It prints out when linting starts
#          and ends, plus the name of each file discovered for linting.
#          Only files ending in '.html' are candidates for linting.
#          This linter could be extended to include other files, such as CSS.
#
# Return code used to sum the rc from individual lint tests
rc=0
#
# Iterate over all HTML files discovered
for f in $(find . -name "*.html"); do
  # Print the filename, then run 'tidy' in quiet mode and discarding stdout
  echo "checking $f"
  tidy -q $f >> /dev/null
  # Sum the rc from tidy with the sum
  rc=$((rc + $?))
done
#
# Exit program using cumulative return code
exit $rc
