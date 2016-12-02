import click
from PIL import Image, ImageDraw, ImageFont
from itertools import product
from math import floor


def get_paper_size(paper_size):
    base_size, number_of_collapse = paper_size

    if base_size == 'A':
        w, h = (841.0, 1188.0)
    elif base_size == 'B':
        w, h = (1030.0, 1456.0)
    else:
        raise Exception
    for _ in range(int(number_of_collapse)):
        if w > h:
            w /= 2
        else:
            h /= 2
    w, h = floor(w), floor(h)
    return min(w, h), max(w, h)


def get_pixel_size(mili, resolution):
    return int(round(mili * resolution / 25.4))


def calc_context_size(w, h, resolution):
    return tuple([get_pixel_size(s, resolution) for s in (w, h)])


SIZES = [''.join(p) for p in product('AB', '0123456')]


@click.command()
@click.argument('bg', click.Path(exists=True, file_okay=UnicodeTranslateError, dir_okay=False))
@click.option('--paper_size', type=click.Choice(SIZES), default='A4')
@click.option('--resolution', type=click.INT, default=200)
@click.option('--karuta_size', type=click.Tuple([int, int]), default=(55, 85))
@click.option('--dist', type=click.STRING, default='dist.png')
def cmd(bg, paper_size, resolution, karuta_size, dist):
    w, h = get_paper_size(paper_size)
    w, h = calc_context_size(w, h, resolution)
    canvas = Image.new('RGB', (w, h), color='white')
    karuta_w, karuta_h = karuta_size
    karuta_w, karuta_h = calc_context_size(karuta_w, karuta_h, resolution)
    karuta = Image.open(bg)
    karuta = karuta.resize((karuta_w, karuta_h))
    karuta_draw = ImageDraw.Draw(karuta)

    margin = get_pixel_size(8, resolution)
    space = get_pixel_size(0.1, resolution)

    draw = ImageDraw.Draw(canvas)
    for x in range(margin, w - karuta_w, karuta_w + space):
        for y in range(margin, h - karuta_h, karuta_h + space):
            canvas.paste(karuta, (x, y))

    x = None
    separate_color = (155, 155, 155)
    for x in range(margin, w - karuta_w, karuta_w + space):
        draw.line([(x - space, 0), (x - space, h)], fill=separate_color, width=space)
    else:
        draw.line([(x + karuta_w, 0), (x + karuta_w, h)], fill=separate_color, width=space)

    y = None
    for y in range(margin, h - karuta_h, karuta_h + space):
        draw.line([(0, y - space), (w, y - space)], fill=separate_color, width=space)
    else:
        draw.line([(0, y + karuta_h), (w, y + karuta_h)], fill=separate_color, width=space)
    canvas.show()
    canvas.save(dist)


if __name__ == '__main__':
    cmd()
