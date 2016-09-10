# -*- coding: utf-8 -*-


class MetadataProperty(object):

    def __init__(self, metadata_model, fk):
        self._fk = fk
        self._metadata_model = metadata_model

    def __repr__(self):
        return '<MetadataProperty: {}>'.format(
            self._metadata_model.__name__,
        )

    def __get__(self, instance, owner):
        if not instance:
            return self

        metadata = {}

        for md in self._metadata_model.query.filter_by(**{self._fk: instance.id}):
            metadata[md.key] = md.value

        return metadata

    def __set__(self, instance, value):
        if not instance:
            return self

        metadata = {}

        for k, v in value.items():
            md = self._metadata_model.create(key=k, value=v, **{self._fk: instance.id})
            metadata[md.key] = md.value
