import click
from PIL import Image, ImageDraw, ImageFont
from itertools import product
from math import floor
import os
import shutil

MAIN_FONT = os.path.join('assets', 'Jiyucho.ttf')
SUB_FONT = os.path.join('assets', 'やさしさゴシック手書き.otf')

FONT_SIZE = int(137 * (55 / 65))
SUB_FONT_SIZE = int(50 * (55 / 65))


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


def make_karuta_image(bg_iamge, main_word, sub_word_1, sub_word_2, karuta_w, karuta_h, main_font, sub_font):
    karuta = Image.open(bg_iamge)
    karuta = karuta.resize((karuta_w, karuta_h))

    sub_text1_w, sub_text1_h = sub_font.getsize(sub_word_1)
    text_w, text_h = main_font.getsize(main_word)
    sub_text2_w, sub_text2_h = sub_font.getsize(sub_word_2)
    karuta_draw = ImageDraw.Draw(karuta)
    karuta_draw.text((karuta_w / 2 - sub_text1_w / 2, karuta_h / 2 - (text_h / 2 + 20 + sub_text2_h)), sub_word_1,
                     fill='black',
                     font=sub_font)
    karuta_draw.text((karuta_w / 2 - text_w / 2, karuta_h / 2 - text_h / 2), main_word, fill='black', font=main_font)
    karuta_draw.text((karuta_w / 2 - sub_text2_w / 2, karuta_h / 2 + (text_h / 2 + 20)), sub_word_2, fill='black',
                     font=sub_font)
    return karuta


def make_karuta_images(bg_image, words_csv, karuta_w, karuta_h, main_font, sub_font):
    for a, b, c in (row.strip().split(',') for row in open(words_csv)):
        yield make_karuta_image(bg_image, b, a, c, karuta_w, karuta_h, main_font, sub_font)


def make_karuta_seats(karuta_images, seat_w, seat_h, karuta_w, karuta_h, resolution):
    margin = get_pixel_size(8, resolution)
    space = get_pixel_size(0.1, resolution)
    separate_color = (155, 155, 155)

    def draw_separate_line(draw_context):
        x = None
        for x in range(margin, seat_w - karuta_w, karuta_w + space):
            draw_context.line([(x - space, 0), (x - space, seat_h)], fill=separate_color, width=space)
        else:
            draw_context.line([(x + karuta_w, 0), (x + karuta_w, seat_h)], fill=separate_color, width=space)
        y = None
        for y in range(margin, seat_h - karuta_h, karuta_h + space):
            draw_context.line([(0, y - space), (seat_w, y - space)], fill=separate_color, width=space)
        else:
            draw_context.line([(0, y + karuta_h), (seat_w, y + karuta_h)], fill=separate_color, width=space)

    canvas = None
    final_output = False
    while True:
        final_output = False
        try:
            canvas = Image.new('RGB', (seat_w, seat_h), color='white')
            for x in range(margin, seat_w - karuta_w, karuta_w + space):
                for y in range(margin, seat_h - karuta_h, karuta_h + space):
                    canvas.paste(karuta_images.__next__(), (x, y))
                    final_output = True
            draw_separate_line(ImageDraw.Draw(canvas))
        except StopIteration:
            break
        yield canvas
    if final_output:
        draw_separate_line(ImageDraw.Draw(canvas))
        yield canvas
    return


@click.command()
@click.argument('bg', click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument('words_csv', click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--paper_size', type=click.Choice(SIZES), default='A4')
@click.option('--resolution', type=click.INT, default=200)
@click.option('--karuta_size', type=click.Tuple([int, int]), default=(85, 55))
@click.option('--dist', type=click.STRING, default='dist')
def cmd(bg, words_csv, paper_size, resolution, karuta_size, dist):
    w, h = get_paper_size(paper_size)
    w, h = calc_context_size(w, h, resolution)
    karuta_w, karuta_h = karuta_size
    karuta_w, karuta_h = calc_context_size(karuta_w, karuta_h, resolution)
    main_font = ImageFont.truetype(MAIN_FONT, size=FONT_SIZE)
    sub_font = ImageFont.truetype(SUB_FONT, size=SUB_FONT_SIZE)
    karuta_images = make_karuta_images(bg, words_csv, karuta_w, karuta_h, main_font, sub_font)

    if os.path.exists(dist):
        shutil.rmtree(dist)
    os.mkdir(dist)
    for idx, seat in enumerate(make_karuta_seats(karuta_images, w, h, karuta_w, karuta_h, resolution), 1):
        output = os.path.join(dist, '{}.png'.format(idx))
        seat.save(output)


if __name__ == '__main__':
    cmd()
