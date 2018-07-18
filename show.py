import argparse
import io

import PIL.Image

import db


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    args = parser.parse_args()
    img_bytes = db.get_image(args.name)
    if not img_bytes:
        print("Not found.")
        return
    image = PIL.Image.open(io.BytesIO(img_bytes))
    image.show()


if __name__ == '__main__':
    main()
