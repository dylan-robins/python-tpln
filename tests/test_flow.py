#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
# *****************************************************************************#

import asyncio
from io import StringIO
from typing import TextIO

import pytest
from tpln import Flow, __version__
from tpln.tasks.base_task import TaskState
from tpln.tasks.sleep_task import Task


class DummyTask(Task):
    def __init__(self, name: str, duration: float = 0, outfile: TextIO | None = None, dependencies: list["Task"] | None = None, group_name: str | None = None) -> None:
        super().__init__(name, dependencies, group_name)
        self.buff = outfile
        self.duration = duration

    async def main(self):
        if self.buff is not None:
            self.buff.write(f"Ran {self.name}" + '\n')
        await asyncio.sleep(self.duration)


def test_version():
    assert __version__ == "0.1.0"

def test_task_registration():
    flow = Flow()
    task = DummyTask(name="DUMMY")
    flow.register_task(task)
    assert len(flow.tasks) == 1
    assert task in flow.tasks

def test_tasks_registration():
    flow = Flow()
    taskA = DummyTask(name="DUMMY")
    taskB = DummyTask(name="DUMMY")
    flow.register_tasks(taskA, taskB)
    assert len(flow.tasks) == 2
    assert set((taskA, taskB)) == flow.tasks

def test_tasks_uuid_lookup():
    flow = Flow()
    task = DummyTask(name="DUMMY")
    flow.register_task(task)

    assert flow.get_task_by_id(task.id) == task

def test_task_group_creation():
    flow = Flow()
    flow.create_task_group("grp", 5)
    assert "grp" in flow.task_groups
    assert isinstance(flow.task_groups["grp"], asyncio.Semaphore)
    assert flow.task_groups["grp"]._value == 5

def test_task_group_duplicates():
    flow = Flow()
    flow.create_task_group("grp", 5)
    with pytest.raises(NameError):
        flow.create_task_group("grp", 2)

def test_iter_predecessors():
    flow = Flow()
    A = DummyTask(name="A")
    B = DummyTask(name="B")
    C = DummyTask(name="C")
    D = DummyTask(name="D", dependencies=[A, B, C])

    flow.register_tasks(A, B, C, D)

    assert set(flow.iter_predecessors(D)) == set((A, B, C))

def test_run_side_effect_fast():
    sio = StringIO("")
    flow = Flow()
    flow.register_task(DummyTask(name="A", outfile=sio))
    
    flow.run()
    
    sio.seek(0)
    assert sio.read() == "Ran A\n"

def test_run_side_effect_slow():
    sio = StringIO("")
    flow = Flow()
    flow.register_task(DummyTask(name="A", duration=2, outfile=sio))
    
    flow.run()
    
    sio.seek(0)
    assert sio.read() == "Ran A\n"

def test_run_side_effect_multiple():
    sio = StringIO("")
    flow = Flow()
    flow.register_task(A := DummyTask(name="A", outfile=sio))
    flow.register_task(DummyTask(name="B", outfile=sio, dependencies=[A]))
    
    flow.run()
    
    sio.seek(0)
    assert sio.read() == "Ran A\nRan B\n"

def test_run_side_effect_multiple_semaphore():
    sio = StringIO("")
    flow = Flow()
    flow.create_task_group("sequential", 1)
    flow.register_task(A := DummyTask(name="A", duration=1, outfile=sio, group_name="sequential"))
    flow.register_task(DummyTask(name="B", duration=1, outfile=sio, dependencies=[A], group_name="sequential"))
    
    flow.run()
    
    sio.seek(0)
    assert sio.read() == "Ran A\nRan B\n"

