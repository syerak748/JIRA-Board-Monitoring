import sys
def processDLDFiles(filepaths):
    for filepath in filepaths:
        print(f'processing file : {filepath}')


if __name__ == "__main__":
    file_paths = sys.argv[1:]
    processDLDFiles(file_paths)