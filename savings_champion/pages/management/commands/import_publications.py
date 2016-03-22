from datetime import datetime
from pages.models import PressAppearancePublication, PressAppearance
import parsedatetime as pdt
from csv import DictReader

with open('csv.csv', 'r') as csv:
    csv = DictReader(csv)
    c = pdt.Constants()
    c.BirthdayEpoch = 80
    p = pdt.Calendar(c)
    PressAppearancePublication.objects.all().delete()
    PressAppearance.objects.all().delete()
    for csv_line, csv_record in enumerate(csv):
        print 'Line: %d' % csv_line
        publication, _ = PressAppearancePublication.objects.get_or_create(name=csv_record['Publication'].strip())
        extracted_date = p.parseDateText(csv_record['Date'])
        PressAppearance(publication=publication, title=csv_record['Title'].strip(), author=csv_record['Author'].strip(), date_featured=datetime(
            *extracted_date[:6])).save()