#!/usr/bin/env python

# Copyright (C) 2018:
#     Sonia Bogos, sonia.bogos@elca.ch
#


import pytest
import logging
import time
import redis

from sh import docker

# logging
logging.basicConfig(
    format='%(asctime)s %'
           '(name)s %(levelname)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p'
)
logger = logging.getLogger("redis_tools.tests.test_redis_service")
logger.setLevel(logging.DEBUG)


@pytest.mark.usefixtures('redis_settings', scope='class')
class TestServiceRedis():
    """
        Class to test the redis service.
    """
    def test_redis(self, redis_settings):
        """
        Test to check if redis is functional.
        :param redis_settings: redis settings, e.g. host, port and password.
        :return:
        """

        redis_port = redis_settings["redis_port"]
        redis_host = redis_settings["redis_host"]
        redis_auth = redis_settings["redis_auth"]
        test_key = "test_key"
        test_value = "test_value"
        test_counter = "ctr"
        test_counter_value = 345

        # test if one can do modifications on redis
        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_auth)
        logger.info("Connecting to the Redis db")

        r.set(test_key, test_value)
        logger.info("Redis : set {key} {value}".format(key=test_key, value=test_value))
        check_value = r.get(test_key).decode('utf-8')
        logger.info("Redis: get {key}".format(key=test_key))

        logger.info("Checking that the the retrieved value is the one that was just inserted")
        assert check_value == test_value

        r.set(test_counter, test_counter_value)
        logger.info("Redis : set {ctr} {value}".format(ctr=test_counter, value=test_counter_value))
        r.incr(test_counter)
        logger.info("Redis: incr {ctr}".format(ctr=test_counter))
        ctr_value = int(r.get(test_counter).decode('utf-8'))

        logger.info("Checking that the value of the counter {ctr} correctly incremented".format(ctr=test_counter))
        assert test_counter_value + 1 == ctr_value

    def test_data_consistency(self, settings, redis_settings):
        """
        Test to check that the modifications done in Redis are present after the container was stopped.
        :param settings: settings of the container, e.g. container name, service name, etc.
        :param redis_settings: redis settings, e.g. host, port and password.
        :return:
        """

        container_name = settings['container_name']
        service_name = settings['service_name']
        redis_port = redis_settings["redis_port"]
        redis_host = redis_settings["redis_host"]
        redis_auth = redis_settings["redis_auth"]
        test_key = "test_key2"
        test_value = "test_value2"

        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_auth)
        logger.info("Connecting to the Redis db")

        r.set(test_key, test_value)
        logger.info("Redis : set {key} {value}".format(key=test_key, value=test_value))

        stop_container = docker.bake("stop", container_name)
        logger.debug(stop_container)
        stop_container()

        restart_container = docker.bake("restart", container_name)
        logger.debug(restart_container)
        restart_container()

        redis_is_up = False

        while redis_is_up == False:
            # check if monit started redis
            time.sleep(1)
            check_service = docker.bake("exec", "-i", container_name, "systemctl", "status", service_name)
            logger.debug(check_service)

            try:
                redis_status = check_service().exit_code
                if redis_status == 0:
                    redis_is_up = True
                    logger.info("{service} is running".format(service=service_name))

            except Exception as e:
                logger.info("{service} is not yet running".format(service=service_name))

        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_auth)
        logger.info("Connecting to the Redis db")

        check_value = r.get(test_key).decode('utf-8')
        logger.info("Redis: get {key}".format(key=test_key))

        logger.info("Checking that the retrieved value is the one that was inserted")
        assert check_value == test_value
