#!/usr/bin/env python
# Copyright (C) 2018:
#     Sonia Bogos, sonia.bogos@elca.ch
#

import pytest
import json

def pytest_addoption(parser):
    parser.addoption("--redis-config-file", action="store", help="Json Redis configuration file ", dest="redis_config_file")
    parser.addoption("--config-file", action="store", help="Json container configuration file ", dest="config_file")

@pytest.fixture()
def settings(pytestconfig):
	try:
		with open(pytestconfig.getoption('config_file')) as json_data:
			config = json.load(json_data)

	except IOError as e:
		raise IOError("Config file {path} not found".format(path=pytestconfig.getoption('config_file')))

	return config


@pytest.fixture()
def redis_settings(pytestconfig):
	try:
		with open(pytestconfig.getoption('redis_config_file')) as json_data:
			config = json.load(json_data)

	except IOError as e:
		raise IOError("Config file {path} not found".format(path=pytestconfig.getoption('redis_config_file')))

	return config
