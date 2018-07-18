# sconedrone

Read the latest post from the Carma's Cafe website, check if mocha
chip scones look like they're on the menu, and send an AWS SNS message
if they are (and if we haven't already sent one today).  Store state in
AWS S3 bucket.

## Usage with AWS Lambda

To add dependencies locally (for uploading the contents of the current
directory as a zip file):

```
pip install -r requirements.txt -t .
```