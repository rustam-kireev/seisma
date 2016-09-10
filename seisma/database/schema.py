# -*- coding: utf-8 -*-

from datetime import date
from datetime import datetime

from sqlalchemy import UniqueConstraint

from .alchemy import alchemy
from .alchemy import ModelMixin
from ..json import ObjectConverter
from .descriptors import MetadataProperty


class Build(alchemy.Model, ModelMixin):

    __tablename__ = 'build'

    id = alchemy.Column(alchemy.Integer, autoincrement=True, primary_key=True)
    created = alchemy.Column(alchemy.Date(), nullable=False, default=date.today)
    name = alchemy.Column(alchemy.String(255), nullable=False, unique=True)
    description = alchemy.Column(alchemy.Text(), nullable=False, default='')
    is_active = alchemy.Column(alchemy.Boolean, nullable=False, default=True)

    to_dict = ObjectConverter(
        ObjectConverter.FromAttribute('name'),
        ObjectConverter.FromAttribute('created'),
        ObjectConverter.FromAttribute('description'),
    )


class Case(alchemy.Model, ModelMixin):

    __tablename__ = 'case'

    id = alchemy.Column(alchemy.Integer, autoincrement=True, primary_key=True)
    build_id = alchemy.Column(alchemy.Integer, alchemy.ForeignKey('build.id'), nullable=False)
    created = alchemy.Column(alchemy.Date(), nullable=False, default=date.today)
    name = alchemy.Column(alchemy.String(255), nullable=False, index=True)
    description = alchemy.Column(alchemy.Text(), nullable=False, default='')

    to_dict = ObjectConverter(
        ObjectConverter.FromAttribute('name'),
        ObjectConverter.FromAttribute('created'),
        ObjectConverter.FromAttribute('description'),
    )


class BuiltResultMetadata(alchemy.Model, ModelMixin):

    __tablename__ = 'build_result_metadata'

    id = alchemy.Column(alchemy.Integer, autoincrement=True, primary_key=True)
    build_result_id = alchemy.Column(alchemy.Integer, alchemy.ForeignKey('build_result.id'), nullable=False)
    key = alchemy.Column(alchemy.String(255), nullable=False)
    value = alchemy.Column(alchemy.Text(), nullable=False)


class BuildResult(alchemy.Model, ModelMixin):

    __tablename__ = 'build_result'

    __table_args__ = (
        UniqueConstraint(
            'name',
            'build_id',
            name='result_of_build',
        ),
    )

    id = alchemy.Column(alchemy.Integer, autoincrement=True, primary_key=True)
    build_id = alchemy.Column(alchemy.Integer, alchemy.ForeignKey('build.id'), nullable=False)
    name = alchemy.Column(alchemy.String(255), nullable=False)
    date = alchemy.Column(alchemy.DateTime(), nullable=False, default=datetime.now)
    tests_count = alchemy.Column(alchemy.Integer, nullable=False, default=0)
    success_count = alchemy.Column(alchemy.Integer, nullable=False, default=0)
    fail_count = alchemy.Column(alchemy.Integer, nullable=False, default=0)
    error_count = alchemy.Column(alchemy.Integer, nullable=False, default=0)
    runtime = alchemy.Column(alchemy.Float(), nullable=False)
    was_success = alchemy.Column(alchemy.Boolean(), nullable=False)
    is_running = alchemy.Column(alchemy.Boolean(), nullable=False, default=True)

    md = MetadataProperty(BuiltResultMetadata, fk='build_result_id')

    to_dict = ObjectConverter(
        ObjectConverter.FromAttribute('name'),
        ObjectConverter.FromAttribute('date'),
        ObjectConverter.FromAttribute('build'),
        ObjectConverter.FromAttribute('runtime'),
        ObjectConverter.FromAttribute('fail_count'),
        ObjectConverter.FromAttribute('is_running'),
        ObjectConverter.FromAttribute('tests_count'),
        ObjectConverter.FromAttribute('error_count'),
        ObjectConverter.FromAttribute('was_success'),
        ObjectConverter.FromAttribute('success_count'),
        ObjectConverter.FromAttribute('md', alias='metadata'),
    )

    @property
    def build(self):
        return Build.query.filter_by(id=self.build_id).first()


class CaseResultMetadata(alchemy.Model, ModelMixin):

    __tablename__ = 'case_result_metadata'

    id = alchemy.Column(alchemy.Integer, autoincrement=True, primary_key=True)
    case_result_id = alchemy.Column(alchemy.Integer, alchemy.ForeignKey('case_result.id'), nullable=False)
    key = alchemy.Column(alchemy.String(255), nullable=False)
    value = alchemy.Column(alchemy.Text(), nullable=False)


class CaseResult(alchemy.Model, ModelMixin):

    __tablename__ = 'case_result'

    id = alchemy.Column(alchemy.Integer, autoincrement=True, primary_key=True)
    case_id = alchemy.Column(alchemy.Integer, alchemy.ForeignKey('case.id'), nullable=False)
    build_result_id = alchemy.Column(alchemy.Integer, alchemy.ForeignKey('build_result.id'), nullable=False)
    date = alchemy.Column(alchemy.DateTime(), nullable=False, default=datetime.now)
    reason = alchemy.Column(alchemy.Text(), nullable=False, default='')
    runtime = alchemy.Column(alchemy.Float(), nullable=False)
    status = alchemy.Column(alchemy.Enum('passed', 'skipped', 'failed', 'error'), nullable=False)

    md = MetadataProperty(CaseResultMetadata, fk='case_result_id')

    to_dict = ObjectConverter(
        ObjectConverter.FromAttribute('date'),
        ObjectConverter.FromAttribute('reason'),
        ObjectConverter.FromAttribute('status'),
        ObjectConverter.FromAttribute('case'),
        ObjectConverter.FromAttribute('runtime'),
        ObjectConverter.FromAttribute('md', alias='metadata'),
    )

    @property
    def case(self):
        return Case.query.filter_by(id=self.case_id).first()
