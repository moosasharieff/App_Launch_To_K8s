import unittest
from unittest import skip  # noqa

from custom_exceptions import AlreadyExistsError
from metric_data_class import (Metric_Data, Metrics_Collector,
                               Pod_CPU_Collector, Pod_NAME_Collector,
                               Pod_Datetime_Collector)


class Test_Metrics_Collector(unittest.TestCase):
    """This class will test various methods in
    cls: MetricsCollector"""
    METRICS_URL = ("http://localhost:8001/apis/metrics.k8s.io/"
                   "v1beta1/namespaces/my-app-namespace/pods")

    def test_get_metrics(self):
        # Initiation
        mc = Metrics_Collector(self.METRICS_URL)
        metrics = mc.get_metrics()

        # Assertions
        self.assertEqual(type(metrics), list)
        self.assertEqual(metrics[0]['metadata']['namespace'],
                         'my-app-namespace')


class Test_Metric_Data(unittest.TestCase, Metric_Data):
    """Tests cls: Pod_CPU_Collector();
    Test CRUD operation on variables.
    """

    def setUp(self):
        super().__init__()

    def test_create_name(self):
        """Test if CRUD operation on var: NAME"""
        self.NAME.add('Sample1')

        # Assertions
        for ele in self.NAME:
            self.assertEqual(ele, 'Sample1')
            self.assertNotIn(ele, 'Sample2')

    def test_delete_name(self):
        """Test if CRUD operation on var: NAME"""
        self.NAME.add('Sample1')
        self.NAME.remove('Sample1')

        # Assertions
        for ele in self.NAME:
            self.assertNotEqual(ele, 'Sample1')

    def test_add_CPU(self):
        self.CPU['cpu_id_01'] = '234567n'

        # Assertions
        self.assertEqual(self.CPU['cpu_id_01'], '234567n')

    def test_delete_CPU(self):
        self.CPU['cpu_id_01'] = '234567n'
        del (self.CPU['cpu_id_01'])

        # Assertions
        with self.assertRaises(KeyError):
            self.CPU['cpu_id_01']

    def test_convert_dub_datetime(self):
        val = self._convert_dub_datetime('2024-12-05T21:58:50Z')

        # Assertions
        self.assertEqual(val, '2024-12-05 21:58:50 GMT+0000')


class Test_Pod_CPU_Collector(unittest.TestCase, Metric_Data):
    METRICS_URL = ("http://localhost:8001/apis/metrics.k8s.io/"
                   "v1beta1/namespaces/my-app-namespace/pods")

    def setUp(self):
        super().__init__()

        # Initiation
        mc = Metrics_Collector(self.METRICS_URL)
        self.metrics = mc.get_metrics()

        self.pod_collector = Pod_CPU_Collector()

    def test_extract(self):
        """Test getting pod name and cpu values for the list
        of pods."""

        cpu_values = self.pod_collector.extract(self.metrics)

        # names of pods
        vals = {}
        for name, dt in cpu_values:
            vals[name] = dt

        # Assertions
        for name, cpu in cpu_values:
            self.assertIn(name, vals)

    def test_get(self):
        """Test returning CPU value when with Pod name."""

        cpu_values = self.pod_collector.extract(self.metrics)

        # Adding pod name and cpu value to dict{}
        for name, val in cpu_values:
            self.pod_collector.add(name, val)

        # Assertion
        for name, val in cpu_values:
            pod_cpu = self.pod_collector.get(name)
            self.assertEqual(pod_cpu, val)

    def test_get_for_raise_keyError(self):
        """Test if we are getting KeyError as expected for
        pod name which does not exist."""

        cpu_values = self.pod_collector.extract(self.metrics)

        # Adding pod name and cpu value to dict{}
        for name, val in cpu_values:
            self.pod_collector.add(name, val)

        # Assertion
        with self.assertRaises(KeyError):
            self.pod_collector.get('testing_pod')

    def test_add(self):
        """Test adding the {pod_name:cpu_value}"""

        cpu_values = self.pod_collector.extract(self.metrics)

        # Adding pod name and cpu value to dict{}
        for name, val in cpu_values:
            self.pod_collector.add(name, val)

        # Assertions
        for name, val in cpu_values:
            self.assertEqual(self.CPU[name], val)

    def test_remove(self):
        """Test removing Pod name from dict(): CPU"""

        # Initiation
        mc = Metrics_Collector(self.METRICS_URL)
        metrics = mc.get_metrics()

        self.pod_collector = Pod_CPU_Collector()
        cpu_values = self.pod_collector.extract(metrics)

        # Adding pod name and cpu value to dict{}
        for name, val in cpu_values:
            self.pod_collector.add(name, val)

        # Removing pod name and cpu value to dict{}
        for name, val in cpu_values:
            self.pod_collector.remove(name)

        # Assertions
        for name, val in cpu_values:
            with self.assertRaises(KeyError):
                self.CPU[name]


class Test_Pod_Name_Collector(unittest.TestCase, Metric_Data):
    """Test Class tests cls: Pod_Name_Collector()"""
    METRICS_URL = ("http://localhost:8001/apis/metrics.k8s.io/"
                   "v1beta1/namespaces/my-app-namespace/pods")

    def setUp(self):
        super().__init__()

        # Initiation
        mc = Metrics_Collector(self.METRICS_URL)
        self.metrics = mc.get_metrics()

        self.pod_collector = Pod_NAME_Collector(self.metrics)

    def test_extract(self):
        """Test getting pod name and cpu values for the list
        of pods."""

        name_values = self.pod_collector.get_all()

        # names of pods
        li = []
        for name in name_values:
            li.append(name)

        # Assertions
        self.assertEqual(len(name_values), len(li))
        for name in name_values:
            self.assertIn(name, li)

    def test_isPresent(self):
        """Test returning CPU value when with Pod name."""

        name_values = self.pod_collector.get_all()

        # uncomment when running single test only
        # this is because pod_names are present in
        # name_value after running previous tests.
        # Adding pod name and cpu value to dict{}
        # for ele in name_values:
        #     self.pod_collector.add(ele)

        # Assertions
        self.assertFalse(self.pod_collector.is_present('Sample_Pod'))

        for name in name_values:
            res = self.pod_collector.is_present(name)
            self.assertTrue(res)

    def test_remove(self):
        """Test removing Pod name from dict(): CPU"""
        name_values = self.pod_collector.get_all()

        # uncomment when running single test only
        # this is because pod_names are present in
        # name_value after running previous tests.
        # for ele in name_values:
        #     self.pod_collector.add(ele)

        # Deleting the pod_name from collection
        name_values = list(name_values)
        self.pod_collector.remove(name_values[0])

        # Assertions
        self.assertFalse(self.pod_collector.is_present(name_values[0]))


class Test_Pod_Datetime_Collector(unittest.TestCase, Metric_Data):
    """Test Class tests cls: Pod_Datetime_Collector()"""
    METRICS_URL = ("http://localhost:8001/apis/metrics.k8s.io/"
                   "v1beta1/namespaces/my-app-namespace/pods")

    def setUp(self):
        super().__init__()

        # Initiation
        mc = Metrics_Collector(self.METRICS_URL)
        self.metrics = mc.get_metrics()

        self.pod_collector = Pod_Datetime_Collector()

    def test_extract(self):
        """Test getting pod name and datetime values for the list
        of pods."""

        dt_values = self.pod_collector.extract(self.metrics)

        # names of pods
        vals = {}
        for name, dt in dt_values:
            vals[name] = dt

        # Assertions
        self.assertEqual(len(dt_values), len(vals))
        for name, dt in dt_values:
            self.assertTrue(str(name))
            self.assertTrue(str(dt))

    def test_add(self):
        """Add test name to the set(): self.NAME"""
        dt_values = self.pod_collector.extract(self.metrics)

        for name, dt in dt_values:
            self.pod_collector.add(name, dt)

        # Assertion
        for name, dt in dt_values:
            self.assertIn(name, self.CREATION_DATETIME)
            self.assertEqual(dt, self.CREATION_DATETIME.get(name))

    def test_datetime_raise_pod_exists_exception(self):
        """Test raising an exception if pod name already
        exists in the self.NAME collection."""
        dt_values = self.pod_collector.extract(self.metrics)

        name, dt = dt_values[0]

        # uncomment when running single test only
        # this is because pod_names are present in
        # dt_value after running previous tests.
        # self.pod_collector.add(name, dt)

        # Assertion
        with self.assertRaises(AlreadyExistsError):
            self.pod_collector.add(name, dt)

    def test_isPresent(self):
        """Test returning CPU value when with Pod name."""

        dt_values = self.pod_collector.extract(self.metrics)

        # uncomment when running single test only
        # this is because pod_names are present in
        # name_value after running previous tests.
        # Adding pod name and cpu value to dict{}
        # for name, dt in dt_values:
        #     self.pod_collector.add(name, dt)

        # Assertions
        self.assertFalse(self.pod_collector.is_present('Sample_Pod'))

        for name, dt in dt_values:
            res = self.pod_collector.is_present(name)
            self.assertTrue(res)

    def test_get(self):
        """Test retrieving Pod's datetime value"""
        dt_values = self.pod_collector.extract(self.metrics)

        # uncomment when running single test only
        # this is because pod_names are present in
        # name_value after running previous tests.
        # for name, dt in dt_values:
        #     self.pod_collector.add(name, dt)

        # Assertions
        for name, dt in dt_values:
            res = self.pod_collector.get(name)
            self.assertEqual(res, dt)

    def test_remove(self):
        """Test removing Pod name from dict(): CPU"""
        dt_values = self.pod_collector.extract(self.metrics)

        # uncomment when running single test only
        # this is because pod_names are present in
        # name_value after running previous tests.
        # for name, dt in dt_values:
        #     self.pod_collector.add(name, dt)

        # Deleting the pod_name from collection
        name, dt = dt_values[0]
        self.pod_collector.remove(name)

        # Assertions
        self.assertFalse(self.pod_collector.is_present(name))


if __name__ == '__main__':
    unittest.main()
