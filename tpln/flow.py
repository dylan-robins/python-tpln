#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
# *****************************************************************************#

from __future__ import annotations

import asyncio as aio
import logging
import multiprocessing
from typing import Iterator
from uuid import UUID

import networkx as nx

from .tasks import Task, TaskState

_logger = logging.getLogger(__name__)


class Flow:
    def __init__(self) -> None:
        self.tasks: set[Task] = set()
        self.graph = nx.DiGraph()
        self.task_groups: dict[str, aio.Semaphore] = {}
        self.event_loop = aio.new_event_loop()
        self.gui_msg_queue = multiprocessing.Queue()

    def register_task(self, task: Task):
        self.tasks.add(task)

        self.graph.add_node(task.id, task_obj=task)
        for dep in task.dependencies:
            self.graph.add_edge(dep.id, task.id)

    def register_tasks(self, *args: Task):
        for task in args:
            self.register_task(task)

    def get_task_by_id(self, id: UUID) -> Task:
        return [task for task in self.tasks if task.id == id][0]

    def create_task_group(self, group_name: str, max_concurrent_tasks: int):
        if group_name in self.task_groups:
            raise NameError(f"task group {group_name} already exists!")

        self.task_groups[group_name] = aio.Semaphore(max_concurrent_tasks)

    def iter_graph(self) -> Iterator[Task]:
        for id in nx.topological_sort(self.graph):
            yield self.graph.nodes[id]["task_obj"]

    def iter_predecessors(self, task: Task) -> list[Task]:
        predecessor_ids = list(self.graph.predecessors(task.id))
        return [other for other in self.tasks if other.id in predecessor_ids]

    def run(self):
        async def _run():
            for task in self.iter_graph():
                _logger.info(f"Scheduling task {task}")

                while not all(
                    predecessor.state == TaskState.done
                    for predecessor in self.iter_predecessors(task)
                ):
                    await aio.sleep(
                        0.5
                    )  # Arbitrary sleep time, should probably be user-configurable

                _logger.info(f"Running {task}...")
                self.event_loop.create_task(task.run(self))

        self.event_loop.run_until_complete(_run())
        remaining_tasks = aio.all_tasks(self.event_loop)
        if len(remaining_tasks) > 0:
            self.event_loop.run_until_complete(aio.gather(*remaining_tasks))
