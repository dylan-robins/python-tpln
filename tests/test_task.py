#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
# *****************************************************************************#

import asyncio as aio

import pytest
from tpln.tasks import Task


def test_bad_task_inheritance():
    class _cust_task(Task):
        pass

    with pytest.raises(TypeError):
        _cust_task("CUSTOM_TASK") # type: ignore


class cust_task(Task):
    async def main(self):
        return self.name


def test_good_task_inheritance():
    task = cust_task("CUSTOM_TASK")
    assert isinstance(task, Task)


def test_task_repr():
    task = cust_task("CUSTOM_TASK")
    assert repr(task) == "CUSTOM_TASK<cust_task>"


def test_task_run():
    task = cust_task("CUSTOM_TASK")
    assert aio.run(task.main()) == "CUSTOM_TASK"
