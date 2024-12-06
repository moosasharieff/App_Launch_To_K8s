import unittest
from unittest import skip  # noqa

from metric_data_class import (Metric_Data, Metrics_Collector,
                               Pod_CPU_Collector)


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

    def test_add_DATETIME(self):
        self.append_datetime_list('2024-12-05T21:58:50Z')
        self.append_datetime_list('2024-12-05T19:38:50Z')
        self.append_datetime_list('2024-12-05T23:35:50Z')

        li = ['2024-12-05T21:58:50Z',
              '2024-12-05T19:38:50Z',
              '2024-12-05T123:35:50Z']
        li.sort()

        # Assertions
        self.assertEqual(len(self.DATETIME_LIST), 3)

    def test_delete_DATETIME(self):
        self.append_datetime_list('2024-12-05T21:58:50Z')
        self.append_datetime_list('2024-12-05T12:38:50Z')
        self.append_datetime_list('2024-12-05T23:35:50Z')

        val = self.DATETIME_LIST[1]
        self.DATETIME_LIST.remove(val)

        # Assertions
        # assert val not in self.DATETIME_LIST
        self.assertNotIn(str(val), self.DATETIME_LIST)


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
        li = ['my-app-56587895ff-smz8s',
              'my-app-deployement-56587895ff-h8ltq',
              'my-app-deployment-699c985fbf-sl69d']

        # Assertions
        for name, cpu in cpu_values:
            self.assertIn(name, li)

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


if __name__ == '__main__':
    unittest.main()
