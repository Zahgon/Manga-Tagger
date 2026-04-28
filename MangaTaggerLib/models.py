import logging
from datetime import datetime
from pytz import timezone

from MangaTaggerLib.errors import MetadataNotCompleteError
from MangaTaggerLib.utils import AppSettings, compare


class Metadata:
    _log = None

    @classmethod
    def fully_qualified_class_name(cls):
        pass

    def __init__(self, manga_title, logging_info, anilist_details=None, details=None):
        Metadata._log = logging.getLogger(self.fully_qualified_class_name())

        self.search_value = manga_title
        Metadata._log.info(f'Creating Metadata model for series "{manga_title}"...', extra=logging_info)

        if anilist_details:  # If details are grabbed from Anilist APIs
            self._construct_api_metadata(anilist_details, logging_info)
        elif details:  # If details were stored in the database
            self._construct_database_metadata(details)
        else:
            Metadata._log.exception(MetadataNotCompleteError, extra=logging_info)
        Metadata._log.debug(f'{self.search_value} Metadata Model: {self.__dict__.__str__()}')

        logging_info['metadata'] = self.__dict__
        Metadata._log.info('Successfully created Metadata model.', extra=logging_info)

    def _construct_api_metadata(self, anilist_details, logging_info):
        pass

    def _construct_database_metadata(self, details):
        pass

    def _construct_publish_date(self, date):
        pass

    def _parse_genres(self, genres, logging_info):
        pass

    def _parse_synonyms(self, synonyms, logging_info):
        pass

    def _parse_staff(self, anilist_staff, logging_info):
        pass

    def _add_anilist_staff_member(self, role, a_staff):
        pass

    def _parse_serializations(self, serializations, logging_info):
        pass

    def test_value(self):
        pass
