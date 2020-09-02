#!/usr/bin/env python

"""Tests for `serveliza` package."""

from datetime import datetime, timedelta
from pandas import pandas as pd
import unittest

from serveliza.roll import ElectoralRoll
from serveliza.roll.printer import RollPrinter
from serveliza.roll.memorizer import RollMemorizer
from serveliza.roll.exporter import RollExporter


class TestServeliza(unittest.TestCase):
    """Tests for `serveliza` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        pass

    def tearDown(self):
        """Tear down test fixtures, if any."""
        pass

    def test_roll_2013(self):
        """Test something."""
        roll = ElectoralRoll(source='tests/fixtures/A0152003.pdf')
        self.roll_assert_props(roll)
        roll.run()
        self.roll_assert_runned(roll)

    def test_roll_2016(self):
        roll = ElectoralRoll(source='tests/fixtures/Antártica.pdf')
        self.roll_assert_props(roll)
        roll.run()
        self.roll_assert_runned(roll)

    def test_roll_2020(self):
        roll = ElectoralRoll(
            source='tests/fixtures/A12202.pdf',
            processor='pdfminersix')
        self.roll_assert_props(roll)
        roll.run()
        self.roll_assert_runned(roll)

    def roll_assert_props(self, roll):
        # operationals
        self.assertFalse(roll.is_runned)
        self.assertEqual(len(roll.metadata), 3)
        self.assertTrue('analysis' in roll.metadata)
        self.assertEqual(len(roll.metadata['analysis']), 3)
        self.assertTrue('started' in roll.metadata['analysis'])
        self.assertTrue('finalized' in roll.metadata['analysis'])
        self.assertEqual(len(roll.metadata['analysis']['durations']), 5)
        for stage, duration in roll.metadata['analysis']['durations'].items():
            self.assertTrue(isinstance(duration, timedelta))
        self.assertTrue('files' in roll.metadata)
        for file, meta in roll.metadata['files'].items():
            self.assertTrue('name' in meta)
            self.assertTrue('relative' in meta)
            self.assertTrue('absolute' in meta)
            self.assertTrue('mtime' in meta)
            self.assertTrue('atime' in meta)
            self.assertTrue('durations' in meta)
        self.assertTrue('rolls' in roll.metadata)
        self.assertTrue(isinstance(roll.printer, RollPrinter))
        self.assertTrue(isinstance(roll.memorizer, RollMemorizer))
        self.assertTrue(isinstance(roll.exporter, RollExporter))

    def roll_assert_runned(self, roll):
        self.assertTrue(roll.is_runned)
        # storage property
        self.assertTrue(bool(roll.rid))
        self.assertTrue(bool(roll.roll))
        self.assertTrue(bool(roll.entries))
        self.assertTrue(bool(roll.fields))
        self.assertTrue(isinstance(roll.to_dataframe, pd.DataFrame))
        metadata = roll.metadata['rolls'][roll.rid]
        self.assertTrue(len(metadata['regions']) > 0)
        self.assertTrue(len(metadata['communes']) > 0)
        self.assertTrue(len(metadata['provinces']) > 0)
        self.assertEqual(metadata['entries']['total'], len(roll.entries))
        # metadata property
        analysis = roll.metadata['analysis']
        self.assertTrue(isinstance(analysis['started'], datetime))
        self.assertTrue(isinstance(analysis['finalized'], datetime))
        self.assertTrue(analysis['durations']['processing'] > timedelta())
        self.assertTrue(analysis['durations']['adapting'] > timedelta())
        self.assertTrue(analysis['durations']['parsing'] > timedelta())
        self.assertTrue(analysis['durations']['memorizing'] > timedelta())
        self.assertTrue(analysis['durations']['exporting'] > timedelta())
