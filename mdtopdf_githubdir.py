import os
import urllib.request
import signal
import argparse
import json
import re
import glob
# this ANSI code lets us erase the current line
ERASE_LINE = "\x1b[2K"


def create_url(url):
    """
    modifying the given url so that it returns JSON data when
    we do a GET requests later in this script
    """

    # extract the dirs name from the given url (e.g master)
    download_dirs = re.findall(r"\/tree\/master\/(.*)", url)[0]

    # extract the branch name from the given url (e.g master)
    branch = re.findall(r"\/tree\/(.*?)\/", url)[0]

    api_url = url.replace("https://github.com", "https://api.github.com/repos")
    api_url = re.sub(r"\/tree\/.*?\/", "/contents/", api_url)

    api_url = api_url + "?ref=" + branch

    return (api_url, download_dirs)


def download(repo_url):
    '''
    recursive download
    '''

    # generate the url which returns the JSON data
    api_url, download_dirs = create_url(repo_url)

    r = urllib.request.urlretrieve(api_url)

    # make a directory with the name which is taken from
    # the actual repo
    os.makedirs(download_dirs, exist_ok=True)

    # total files count
    total_files = 0

    with open(r[0], "r") as f:
        raw_data = f.read()

        data = json.loads(raw_data)

        # getting the total number of files so that we
        # can use it for the output information later
        total_files += len(data)

        for index, file in enumerate(data):
            file_url = file["download_url"]
            fname = file["name"]

            path = file["path"]

            if not file_url is None:
                try:
                    # download the file
                    urllib.request.urlretrieve(file_url, path)

                    # bring the cursor to the beginning, erase the current line, and dont make a new line
                    print("\r" + ERASE_LINE, end="")
                    print("\033[1;92m▶ Downloaded: \033[0m{}".format(
                        fname), end="", flush=True)

                except KeyboardInterrupt:
                    # when CTRL+C is pressed during the execution of this script,
                    # bring the cursor to the beginning, erase the current line, and dont make a new line
                    print("\r" + ERASE_LINE, end="")

                    print("\033[1;92m✔ Got interupted\033[0m")
                    print(path)
                    exit()
            else:
                download(file["html_url"])

    return total_files


def main():
    # disbale CTRL+Z
    signal.signal(signal.SIGTSTP, signal.SIG_IGN)

    parser = argparse.ArgumentParser(
        description="Download directories/folders from GitHub")
    parser.add_argument('url', action="store")

    args = parser.parse_args()

    repo_url = args.url
    path = repo_url.split('/')[-1]
    total_files = download(repo_url)

    print("\r" + ERASE_LINE, end="")
    print("\033[1;92m✔ Download complete\033[0m")
    print(path)
    files = glob.glob("./{}/*.md".format(path))
    print(files)
    with open('tmp.md', 'w+') as f:
        for file in files:
            f.write(open(file).read())
    os.system('md2pdf tmp.md test.pdf')


if __name__ == "__main__":
    main()