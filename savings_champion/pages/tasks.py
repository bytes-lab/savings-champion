import os
from PIL import Image
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype
from django.conf import settings
from pages.models import Award
from celery import shared_task

@shared_task()
def create_award_image(award_id, year=True, ranking=False, details=False):
    award = Award.objects.get(pk=award_id)
    image_path = os.path.join(settings.STATIC_ROOT, 'img', 'awards', '%s.png' % (str(award.awarded_date.year)))
    if not ranking:
        template_path = os.path.join(settings.STATIC_ROOT, 'img', 'awards', 'template_small.png')
    else:
        template_path = os.path.join(settings.STATIC_ROOT, 'img', 'awards', 'template.png')
    image_file = Image.open(template_path)
    image = Draw(image_file)
    if details:
        draw_text_in_area(image, (0, 10), (1041, 125), award.category.title)
    if year:
        draw_text_in_area(image, (0, 412), (1041, 527), "Awards %s" % str(award.awarded_date.year))
    if details:
        draw_text_in_area(image, (0, 528), (1041, 759), str(award.get_ranking_display()).upper())
        image_path = os.path.join(settings.STATIC_ROOT, 'img', 'awards', '%s-%s-%s-image.png' % (award.get_ranking_display(),
                                                                                             award.category.title.replace(' ', '_'),
                                                                                             award.awarded_date))
    elif ranking:
        draw_text_in_area(image, (0, 528), (1041, 759), str(award.get_ranking_display()).upper())
        image_path = os.path.join(settings.STATIC_ROOT, 'img', 'awards', '%s-%s.png' % (award.awarded_date.year,
                                                                                        award.get_ranking_display()))
    del image
    image_file.save(image_path, 'PNG')
    return True, image_path

def draw_text_in_area(image, start_coord, end_coord, text):
    width = end_coord[0] - start_coord[0]
    height = end_coord[1] - start_coord[1]
    font, left_border, top_border = fit_text_in_area(width=width, height=height, text=text)
    image.text((start_coord[0] + left_border, start_coord[1] + top_border), text=text, font=font, fill='white')


def fit_text_in_area(width, height, text):
    safe_width = width * 0.9  # 10% border for cleanliness
    safe_height = height * 0.9
    font_path = os.path.join(settings.STATIC_ROOT, 'font', 'LiberationSans-Regular.ttf')
    size = 0
    font = truetype(filename=font_path, size=size)
    while not font.getsize(text=text)[0] > safe_width and not (font.getsize(text=text)[1] * 1.25) > safe_height:
        size += 1
        del font
        font = truetype(filename=font_path, size=size)
    size -= 1
    del font
    font = truetype(filename=font_path, size=size)
    left_border = (width - font.getsize(text=text)[0]) / 2
    top_border = height / 2 - font.getsize(text=text)[1]   # prefer border on bottom, due to text height inaccuracy
    return font, left_border, top_border