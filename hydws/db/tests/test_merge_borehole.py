# Copyright (C) 2019, ETH Zurich - Swiss Seismological Service SED
"""
Well related test facilities.
"""

import datetime
import unittest
import uuid

import hydws.db.orm as dm
import hydws.db.base as base


class BoreholeTestCase(unittest.TestCase):
    """
    Test cases for :py:class:`ramsis.datamodel.well.Borehole`.
    """
    def test_snapshot_no_filter(self):
        dt = datetime.datetime(2020, 1, 1)
        interval = datetime.timedelta(seconds=3600)
        num_samples = 7
        delta_flow = 0.1
        samples = [
            dm.HydraulicSample(datetime_value=dt + i * interval,
                               topflow_value=i,
                               bottomflow_value=i - delta_flow)
            for i in range(num_samples)]
        s0 = dm.BoreholeSection(toplongitude_value=8.925293642,
                                toplatitude_value=46.90669014,
                                topaltitude_value=0,
                                bottomlongitude_value=9,
                                bottomlatitude_value=47,
                                bottomaltitude_value=-500,
                                measureddepth_value=500,
                                holediameter_value=0.3,
                                casingdiameter_value=0.25,
                                _hydraulics=samples)
        bh = dm.Borehole(
            longitude_value=8.925,
            latitude_value=46.906,
            publicid=str(uuid.uuid4()),
            _sections=[s0, ])

        snap = bh.snapshot()

        self.assertNotEqual(id(bh), id(snap))
        self.assertEqual(bh.publicid, snap.publicid)
        self.assertNotEqual(id(bh._sections[0]), id(snap._sections[0]))

        bh_hydraulics = bh._sections[0]._hydraulics
        snap_hydraulics = snap._sections[0]._hydraulics
        self.assertNotEqual(id(bh_hydraulics), id(snap_hydraulics))
        self.assertEqual(bh_hydraulics, snap_hydraulics)

    def test_snapshot_sample_filter(self):
        dt = datetime.datetime(2020, 1, 1)
        interval = datetime.timedelta(seconds=3600)
        num_samples = 7
        delta_flow = 0.1
        samples = [
            dm.HydraulicSample(datetime_value=dt + i * interval,
                               topflow_value=i,
                               bottomflow_value=i - delta_flow)
            for i in range(num_samples)]
        s0 = dm.BoreholeSection(toplongitude_value=8.925293642,
                                toplatitude_value=46.90669014,
                                topaltitude_value=0,
                                bottomlongitude_value=9,
                                bottomlatitude_value=47,
                                bottomaltitude_value=500,
                                holediameter_value=0.3,
                                casingdiameter_value=0.25,
                                _hydraulics=samples)
        bh = dm.Borehole(
            longitude_value=8.925,
            latitude_value=46.906,
            publicid=str(uuid.uuid4()),
            _sections=[s0, ])

        def remove_last(s):
            return s.topflow_value != 6

        snap = bh.snapshot(sample_filter_cond=remove_last)

        self.assertNotEqual(id(bh), id(snap))
        self.assertEqual(bh.publicid, snap.publicid)
        self.assertNotEqual(id(bh._sections[0]), id(snap._sections[0]))

        bh_hydraulics = bh._sections[0]._hydraulics
        snap_hydraulics = snap._sections[0]._hydraulics
        self.assertNotEqual(id(bh_hydraulics), id(snap_hydraulics))
        self.assertNotEqual(bh_hydraulics, snap_hydraulics)
        self.assertEqual(7, len(bh_hydraulics))
        self.assertEqual(6, len(snap_hydraulics))

    def test_snapshot_section_filter(self):
        dt = datetime.datetime(2020, 1, 1)
        interval = datetime.timedelta(seconds=3600)
        num_samples = 7
        delta_flow = 0.1
        samples = [
            dm.HydraulicSample(datetime_value=dt + i * interval,
                               topflow_value=i,
                               bottomflow_value=i - delta_flow)
            for i in range(num_samples)]
        s0 = dm.BoreholeSection(toplongitude_value=8.925293642,
                                toplatitude_value=46.90669014,
                                topaltitude_value=0,
                                bottomlongitude_value=9,
                                bottomlatitude_value=47,
                                bottomaltitude_value=-500,
                                holediameter_value=0.3,
                                casingdiameter_value=0.25,
                                _hydraulics=samples)
        s1 = dm.BoreholeSection(toplongitude_value=9,
                                toplatitude_value=47,
                                topaltitude_value=-500,
                                bottomlongitude_value=9.01,
                                bottomlatitude_value=47.01,
                                bottomaltitude_value=1500,
                                holediameter_value=0.25,
                                casingdiameter_value=0)

        bh = dm.Borehole(
            longitude_value=8.925,
            latitude_value=46.906,
            publicid=str(uuid.uuid4()),
            _sections=[s0, s1, ])

        def remove_lower_section(s):
            return (s.topaltitude_value == 0 and
                    s.bottomaltitude_value == -500)

        snap = bh.snapshot(section_filter_cond=remove_lower_section)

        self.assertNotEqual(id(bh), id(snap))
        self.assertEqual(bh.publicid, snap.publicid)
        self.assertEqual(2, len(bh._sections))
        self.assertEqual(1, len(snap._sections))
        self.assertNotEqual(id(bh._sections[0]), id(snap._sections[0]))

        bh_hydraulics = bh._sections[0]._hydraulics
        snap_hydraulics = snap._sections[0]._hydraulics
        self.assertNotEqual(id(bh_hydraulics), id(snap_hydraulics))
        self.assertEqual(bh_hydraulics, snap_hydraulics)

    def test_merge_update_mutable(self):
        bh_id = str(uuid.uuid4())
        dt = datetime.datetime(2020, 1, 1)
        delta = datetime.timedelta(days=365)

        creation_info = base.CreationInfo(creationtime=dt)
        creation_info_next = base.CreationInfo(creationtime=dt + delta)
        bh0 = dm.Borehole(
            longitude_value=8.925,
            latitude_value=46.906,
            publicid=bh_id,
            _creationinfo=creation_info)

        bh1 = dm.Borehole(
            longitude_value=8.925,
            latitude_value=46.906,
            publicid=bh_id,
            _creationinfo=creation_info_next)

        bh0.merge(bh1)

        self.assertEqual(bh0._creationinfo.creationtime, dt + delta)

    def test_merge_update_section(self):
        bh_id = str(uuid.uuid4())
        dt = datetime.datetime(2020, 1, 1)
        delta = datetime.timedelta(days=365)

        sec_id = str(uuid.uuid4())
        s0 = dm.BoreholeSection(publicid=sec_id,
                                starttime=dt,
                                endtime=None)
        s1 = dm.BoreholeSection(publicid=sec_id,
                                starttime=dt,
                                endtime=dt + delta)

        bh0 = dm.Borehole(
            longitude_value=8.925,
            latitude_value=46.906,
            publicid=bh_id,
            _sections=[s0, ])

        bh1 = dm.Borehole(
            longitude_value=8.925,
            latitude_value=46.906,
            publicid=bh_id,
            _sections=[s1, ])

        bh0.merge(bh1)

        self.assertEqual(bh0._sections[0].endtime, dt + delta)

    def test_merge_append_section(self):
        bh_id = str(uuid.uuid4())
        dt = datetime.datetime(2020, 1, 1)
        delta = datetime.timedelta(days=365)

        sec_id0 = str(uuid.uuid4())
        s0 = dm.BoreholeSection(publicid=sec_id0,
                                starttime=dt,
                                endtime=None)
        sec_id1 = str(uuid.uuid4())
        s1 = dm.BoreholeSection(publicid=sec_id1,
                                starttime=dt + delta,
                                endtime=None)

        bh0 = dm.Borehole(
            longitude_value=8.925,
            latitude_value=46.906,
            publicid=bh_id,
            _sections=[s0, ])

        bh1 = dm.Borehole(
            longitude_value=8.925,
            latitude_value=46.906,
            publicid=bh_id,
            _sections=[s1, ])

        bh0.merge(bh1)

        self.assertEqual(len(bh0._sections), 2)

    def test_merge_to_empty(self):
        bh0 = dm.Borehole(
            longitude_value=8.925,
            latitude_value=46.906)

        bh_id = str(uuid.uuid4())
        sec_id = str(uuid.uuid4())
        dt = datetime.datetime(2020, 1, 1)
        s0 = dm.BoreholeSection(publicid=sec_id,
                                starttime=dt,
                                endtime=None,
                                toplongitude_value=8.925293642,
                                toplatitude_value=46.90669014,
                                topaltitude_value=0,
                                bottomlongitude_value=9,
                                bottomlatitude_value=47,
                                bottomaltitude_value=-500,
                                holediameter_value=0.3,
                                casingdiameter_value=0.25)
        bh1 = dm.Borehole(
            longitude_value=8.925,
            latitude_value=46.906,
            publicid=bh_id,
            _sections=[s0, ])

        bh0.merge(bh1, merge_undefined=True)

        self.assertEqual(bh0.publicid, bh1.publicid)
        self.assertEqual(len(bh0._sections), 1)
        self.assertEqual(len(bh1._sections), 0)


class BoreholeSectionTestCase(unittest.TestCase):
    """
    Test cases for :py:class:`ramsis.datamodel.well.BoreholeSection`.
    """

    def test_merge_update_mutable(self):
        dt = datetime.datetime(2020, 1, 1)
        interval = datetime.timedelta(seconds=3600)
        num_samples = 7
        delta_flow = 0.1
        samples = [
            dm.HydraulicSample(datetime_value=dt + i * interval,
                               topflow_value=i,
                               bottomflow_value=i - delta_flow)
            for i in range(num_samples)]
        sec_id = str(uuid.uuid4())
        s0 = dm.BoreholeSection(publicid=sec_id,
                                starttime=dt,
                                endtime=None,
                                toplongitude_value=8.925293642,
                                toplatitude_value=46.90669014,
                                topaltitude_value=0,
                                bottomlongitude_value=9,
                                bottomlatitude_value=47,
                                bottomaltitude_value=-500,
                                holediameter_value=0.3,
                                casingdiameter_value=0.25,
                                _hydraulics=samples)
        s1 = dm.BoreholeSection(publicid=sec_id,
                                starttime=dt,
                                endtime=dt + (num_samples - 1) * interval,
                                toplongitude_value=8.925293642,
                                toplatitude_value=46.90669014,
                                topaltitude_value=0,
                                bottomlongitude_value=9,
                                bottomlatitude_value=47,
                                bottomaltitude_value=500,
                                holediameter_value=0.3,
                                casingdiameter_value=0.25)

        s0.merge(s1)

        self.assertEqual(s0.endtime, dt + (num_samples - 1) * interval)
        self.assertEqual(len(samples), len(s0._hydraulics))

    def test_merge_append_samples(self):
        dt0 = datetime.datetime(2020, 1, 1)
        interval = datetime.timedelta(seconds=3600)
        num_samples = 7
        delta_flow = 0.1
        samples0 = [
            dm.HydraulicSample(datetime_value=dt0 + i * interval,
                               topflow_value=i,
                               bottomflow_value=i - delta_flow)
            for i in range(num_samples)]

        dt1 = datetime.datetime(2021, 1, 1)
        samples1 = [
            dm.HydraulicSample(datetime_value=dt1 + i * interval,
                               topflow_value=i,
                               bottomflow_value=i - delta_flow)
            for i in range(num_samples)]

        sec_id = str(uuid.uuid4())
        s0 = dm.BoreholeSection(publicid=sec_id,
                                starttime=dt0,
                                endtime=None,
                                toplongitude_value=8.925293642,
                                toplatitude_value=46.90669014,
                                topaltitude_value=0,
                                bottomlongitude_value=9,
                                bottomlatitude_value=47,
                                bottomaltitude_value=-500,
                                holediameter_value=0.3,
                                casingdiameter_value=0.25,
                                _hydraulics=samples0)
        s1 = dm.BoreholeSection(publicid=sec_id,
                                starttime=dt1,
                                endtime=None,
                                toplongitude_value=8.925293642,
                                toplatitude_value=46.90669014,
                                topaltitude_value=0,
                                bottomlongitude_value=9,
                                bottomlatitude_value=47,
                                bottomaltitude_value=-500,
                                holediameter_value=0.3,
                                casingdiameter_value=0.25,
                                _hydraulics=samples1)

        s0.merge(s1)

        self.assertEqual(s0.starttime, dt0)
        self.assertEqual(len(s0._hydraulics),
                         len(samples0) + len(samples1))
        self.assertEqual(s0._hydraulics[0].datetime_value, dt0)
        self.assertEqual(s0._hydraulics[-1].datetime_value,
                         dt1 + (num_samples - 1) * interval)

class HydraulicsSectionTestCase(unittest.TestCase):
    """
    Test cases for :py:class:`ramsis.datamodel.hydraulics.Hydraulics`.
    """

    def test_merge_overlap_by_time(self):
        h1_first_sample = datetime.datetime(2020, 1, 1)
        h1_interval = datetime.timedelta(seconds=3600)
        h1_num_samples = 7

        h1 = dm.BoreholeSection(
            topclosed=False,
            bottomclosed=False,
            starttime=datetime.datetime(2020, 1, 1, 1),
            _hydraulics=[dm.HydraulicSample(
                datetime_value=h1_first_sample + i * h1_interval)
                for i in range(h1_num_samples)])

        h2_first_sample = datetime.datetime(2020, 1, 1, 3)
        h2_interval = datetime.timedelta(seconds=1800)
        h2_num_samples = 4

        h2 = dm.BoreholeSection(
            topclosed=False,
            bottomclosed=False,
            starttime=datetime.datetime(2020, 1, 1, 1),
            _hydraulics=[dm.HydraulicSample(
                datetime_value=h2_first_sample + i * h2_interval)
                for i in range(h2_num_samples)])

        h1.merge(h2)
        self.assertEqual(
            dm.HydraulicSample(datetime_value=datetime.datetime(2020, 1, 1)),
            h1._hydraulics[0])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 1)),
            h1._hydraulics[1])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 2)),
            h1._hydraulics[2])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 5)),
            h1._hydraulics[3])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 6)),
            h1._hydraulics[4])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 3)),
            h1._hydraulics[5])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 3, 30)),
            h1._hydraulics[6])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 4)),
            h1._hydraulics[7])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 4, 30)),
            h1._hydraulics[8])

    def test_merge_empty(self):
        h1_first_sample = datetime.datetime(2020, 1, 1)
        h1_interval = datetime.timedelta(seconds=3600)
        h1_num_samples = 7

        h1 = dm.BoreholeSection(
            topclosed=False,
            bottomclosed=False,
            starttime=datetime.datetime(2020, 1, 1, 1),
            _hydraulics=[dm.HydraulicSample(
                datetime_value=h1_first_sample + i * h1_interval)
                for i in range(h1_num_samples)])

        h2 = dm.BoreholeSection(
            topclosed=False,
            bottomclosed=False,
            starttime=datetime.datetime(2020, 1, 1, 1))

        h1.merge(h2)
        self.assertEqual(
            dm.HydraulicSample(datetime_value=datetime.datetime(2020, 1, 1)),
            h1._hydraulics[0])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 1)),
            h1._hydraulics[1])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 2)),
            h1._hydraulics[2])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 3)),
            h1._hydraulics[3])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 4)),
            h1._hydraulics[4])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 5)),
            h1._hydraulics[5])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 6)),
            h1._hydraulics[6])

    def test_merge_single(self):
        h1_first_sample = datetime.datetime(2020, 1, 1)
        h1_interval = datetime.timedelta(seconds=3600)
        h1_num_samples = 7

        h1 = dm.BoreholeSection(
            topclosed=False,
            bottomclosed=False,
            starttime=datetime.datetime(2020, 1, 1, 1),
            _hydraulics=[dm.HydraulicSample(
                datetime_value=h1_first_sample + i * h1_interval)
                for i in range(h1_num_samples)])

        h2 = dm.BoreholeSection(
            topclosed=False,
            bottomclosed=False,
            starttime=datetime.datetime(2020, 1, 1, 1),
            _hydraulics=[dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 3))])

        h1.merge(h2)
        self.assertEqual(
            dm.HydraulicSample(datetime_value=datetime.datetime(2020, 1, 1)),
            h1._hydraulics[0])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 1)),
            h1._hydraulics[1])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 2)),
            h1._hydraulics[2])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 4)),
            h1._hydraulics[3])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 5)),
            h1._hydraulics[4])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 6)),
            h1._hydraulics[5])
        self.assertEqual(
            dm.HydraulicSample(
                datetime_value=datetime.datetime(2020, 1, 1, 3)),
            h1._hydraulics[6])

def suite():
    suite = unittest.makeSuite(BoreholeTestCase, 'test')
    suite.addTest(
        unittest.makeSuite(BoreholeSectionTestCase, 'test'))
    suite.addTest(
        unittest.makeSuite(HydraulicsSectionTestCase, 'test'))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
