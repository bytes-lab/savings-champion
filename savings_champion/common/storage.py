from storages.backends.s3boto import S3BotoStorage
from django.contrib.staticfiles.storage import ManifestFilesMixin, CachedFilesMixin
from pipeline.storage import PipelineMixin

import urllib, urlparse


class S3PipelineManifestStorage(PipelineMixin, ManifestFilesMixin, S3BotoStorage):
    def hashed_name(self, name, content=None):
        try:
            out = super(S3PipelineManifestStorage, self).hashed_name(name, content)
        except ValueError:
            # This means that a file could not be found, and normally this would
            # cause a fatal error, which seems rather excessive given that
            # some packages have missing files in their css all the time.
            out = name
        return out

class S3PipelineCachedStorage(PipelineMixin, CachedFilesMixin, S3BotoStorage):
    def hashed_name(self, name, content=None):
        try:
            out = super(S3PipelineCachedStorage, self).hashed_name(name, content)
        except ValueError:
            # This means that a file could not be found, and normally this would
            # cause a fatal error, which seems rather excessive given that
            # some packages have missing files in their css all the time.
            out = name
        return out
