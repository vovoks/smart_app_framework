# coding: utf-8
import unittest
from collections import namedtuple
from unittest.mock import Mock
from time import time
from collections import OrderedDict

from scenarios.behaviors.behaviors import Behaviors


class BehaviorsTest(unittest.TestCase):
    def setUp(self):
        self.user = Mock()
        self.user.settings = Mock()
        self.user.settings.app_name = "app_name"
        self.description = Mock()
        self.description.timeout = Mock(return_value=10)
        self.success_action = Mock()
        self.success_action.run = Mock()
        self.fail_action = Mock()
        self.timeout_action = Mock()

        self.description.success_action = self.success_action
        self.description.fail_action = self.fail_action
        self.description.timeout_action = self.timeout_action
        self.descriptions = {"test": self.description}
        self._callback = namedtuple('Callback', 'behavior_id expire_time scenario_id')

    def test_success(self):
        callback_id = "123"
        behavior_id = "test"
        item = {"behavior_id": behavior_id, "expire_time": 2554416000, "scenario_id": None, "text_preprocessing_result": {}}
        items = {str(callback_id): item}
        behaviors = Behaviors(items, self.descriptions, self.user)
        behaviors.success(callback_id)
        #self.success_action.run.assert_called_once_with(self.user, TextPreprocessingResult({}))
        self.success_action.run.assert_called_once()
        self.assertDictEqual(behaviors.raw, {})

    def test_success_2(self):
        callback_id = "123"
        items = {}
        behaviors = Behaviors(items, self.descriptions, self.user)
        behaviors.success(callback_id)
        self.success_action.run.assert_not_called()

    def test_fail(self):
        callback_id = "123"
        behavior_id = "test"
        item = {"behavior_id": behavior_id, "expire_time": 2554416000, "scenario_id": None}
        items = {str(callback_id): item}
        behaviors = Behaviors(items, self.descriptions, self.user)
        behaviors.fail(callback_id)
        self.fail_action.run.assert_called_once()
        self.assertDictEqual(behaviors.raw, {})

    def test_timeout(self):
        callback_id = "123"
        behavior_id = "test"
        item = {"behavior_id": behavior_id, "expire_time": 2554416000, "scenario_id": None}
        items = {str(callback_id): item}
        behaviors = Behaviors(items, self.descriptions, self.user)
        behaviors.timeout(callback_id)
        self.timeout_action.run.assert_called_once()
        self.assertDictEqual(behaviors.raw, {})

    def test_expire(self):
        callback_id = "123"
        behavior_id = "test"
        item = {"behavior_id": behavior_id, "expire_time": 1548079039, "scenario_id": None}
        items = {str(callback_id): item}
        behaviors = Behaviors(items, self.descriptions, self.user)
        behaviors.expire()
        self.assertDictEqual(behaviors.raw, {})

    def test_add_1(self):
        items = {}
        behaviors = Behaviors(items, self.descriptions, self.user)
        callback_id = "123"
        behavior_id = "test"
        text_preprocessing_result = {}
        behaviors.add(callback_id, behavior_id)
        _time = int(time()) + self.description.timeout(None) + Behaviors.EXPIRATION_DELAY

        exp = OrderedDict(behavior_id=behavior_id, expire_time=_time, scenario_id=None,
                          text_preprocessing_result=text_preprocessing_result, action_params=None)
        self.assertDictEqual(behaviors.raw, {callback_id: exp})

    def test_add_2(self):
        items = {}
        behaviors = Behaviors(items, self.descriptions, self.user)
        callback_id = "123"
        behavior_id = "test"
        scenario_id = "test_scen"
        text_preprocessing_result = {"test_scen": 1}

        behaviors.add(callback_id, behavior_id, scenario_id, text_preprocessing_result)
        _time = int(time()) + self.description.timeout(None) + Behaviors.EXPIRATION_DELAY
        exp = OrderedDict(behavior_id=behavior_id, expire_time=_time, scenario_id=scenario_id,
                          text_preprocessing_result=text_preprocessing_result, action_params=None)
        self.assertDictEqual(behaviors.raw, {callback_id: exp})

    def test_check_1(self):
        callback_id = "123"
        behavior_id = "test"
        item = {"behavior_id": behavior_id, "expire_time": 1548079039, "scenario_id": None}
        items = {str(callback_id): item}
        behaviors = Behaviors(items, self.descriptions, self.user)
        self.assertTrue(behaviors.check_got_saved_id(behavior_id))

    def test_check_2(self):
        callback_id = "123"
        behavior_id = "test"
        item = {"behavior_id": behavior_id, "expire_time": 1548079039, "scenario_id": None}
        items = {str(callback_id): item}
        behaviors = Behaviors(items, self.descriptions, self.user)
        with self.assertRaises(KeyError):
            behaviors.check_got_saved_id("test2")

    def test_check_misstate_1(self):
        callback_id = "123"
        behavior_id = "test"
        scenario_id = "test_scen"
        item = {"behavior_id": behavior_id, "expire_time": 1548079039, "scenario_id": scenario_id}
        items = {str(callback_id): item}
        self.user.last_scenarios = Mock()
        self.user.last_scenarios.last_scenario_name = "test_scen2"
        behaviors = Behaviors(items, self.descriptions, self.user)
        self.assertTrue(behaviors.check_misstate(callback_id))

    def test_check_misstate_2(self):
        callback_id = "123"
        behavior_id = "test"
        scenario_id = "test_scen"
        item = {"behavior_id": behavior_id, "expire_time": 1548079039, "scenario_id": scenario_id}
        items = {str(callback_id): item}
        self.user.last_scenarios = Mock()
        self.user.last_scenarios.last_scenario_name = "test_scen"
        behaviors = Behaviors(items, self.descriptions, self.user)
        self.assertFalse(behaviors.check_misstate(callback_id))

    def test_raw(self):
        callback_id = "123"
        behavior_id = "test"
        scenario_id = "test_scen"
        text_preprocessing_result = {1: 2}

        item = {"behavior_id": behavior_id, "expire_time": 1548079039, "scenario_id": scenario_id,
                "text_preprocessing_result": text_preprocessing_result}

        items = {str(callback_id): item}
        behaviors = Behaviors(items, self.descriptions, self.user)
        expected = OrderedDict(behavior_id=behavior_id, expire_time=1548079039, scenario_id=scenario_id,
                               text_preprocessing_result=text_preprocessing_result, action_params={})
        self.assertEqual(behaviors.raw, {callback_id: expected})
