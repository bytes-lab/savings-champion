import datetime
import bz2
import os
from django.conf import settings
from django.core.mail import send_mail

__author__ = 'josh'

from django.core.management.base import BaseCommand
from products.salesforce import SalesforceProductTier, SalesforceOldProductTier


class Command(BaseCommand):
    args = u'<days>'
    help = u'Updates from Salesforce the last x days of changes'

    def handle(self, *args, **options):

        send_mail(u'[Salesforce Mirror System] - Starting {now}'.format(now=datetime.datetime.now().strftime(u'%Y-%m-%d %H:%M:%s')),
                  u'',
                  u'the.website@savingschampion.co.uk',
                  [u'data.team@savingschampion.co.uk'],
                  fail_silently=True)

        spto = SalesforceProductTier()

        spro = spto.provider
        spro.update_recent(*args)
        spro_log = u"\n".join(spro.get_log())
        spro.reset_log()
        if settings.DEBUG:
            self.stdout.write(spro_log)

        spo = spto.product
        spo.update_recent(*args)
        spo_log = u"\n".join(spo.get_log())
        spo.reset_log()
        if settings.DEBUG:
            self.stdout.write(spo_log)

        spto.update_recent(*args)
        spto_log = u"\n".join(spto.get_log())
        spto.reset_log()
        if settings.DEBUG:
            self.stdout.write(spto_log)

        spoto = SalesforceOldProductTier()
        spoto.update_recent(*args)
        spoto_log = u"\n".join(spoto.get_log())
        spoto.reset_log()
        if settings.DEBUG:
            self.stdout.write(spoto_log)

        from boto.s3 import bucket, connection, key

        connection_object = connection.S3Connection(aws_access_key_id=settings.AWS_CREDENTIALS[u's3'][u'access_id'],
                                                    aws_secret_access_key=settings.AWS_CREDENTIALS[u's3'][u'secret_key'])

        bucket_object = bucket.Bucket(connection=connection_object, name=u'salesforce-mirror-system')

        now = datetime.datetime.now().strftime(u'%Y-%m-%d %H:%M:%s')

        filename = u'log_{date}.log.bz2'.format(date=now)

        key_object = key.Key(bucket=bucket_object, name=filename)

        data = u'\n\n'.join([spto_log, spo_log, spro_log, spoto_log]).encode(u'utf8')

        output = bz2.BZ2File(u'/tmp/{filename}'.format(filename=filename), u'wb')

        try:
            output.write(data)
        finally:
            output.close()

        key_object.set_contents_from_filename(u'/tmp/{filename}'.format(filename=filename), reduced_redundancy=True)

        os.remove(u'/tmp/{filename}'.format(filename=filename))

        key_object.set_acl(u'public-read')

        url = key_object.generate_url(expires_in=0, query_auth=False)

        send_mail(subject=u'[Salesforce Mirror System] - Ending {now}'.format(now=datetime.datetime.now().strftime(u'%Y-%m-%d %H:%M:%s')),
                  message=u'Log stored at: {url}'.format(url=url),
                  from_email=u'the.website@savingschampion.co.uk',
                  recipient_list=[u'data.team@savingschampion.co.uk']
                  )