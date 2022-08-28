#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
# *****************************************************************************#

import asyncio as aio
import logging
from time import sleep

import matplotlib.pyplot as plt
import networkx as nx

from .flow import Flow
from .flow_gui import FlowVisualizer
from .tasks import ShellTask, SleepTask, TaskState


def example_flow():
    logging.basicConfig(level=logging.DEBUG, format="### %(levelname)s: %(message)s")
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)

    flow = Flow()
    flow.create_task_group("workers", 2)

    preprocess_task = ShellTask(name="Preprocess", command="ls -la")

    a_task = SleepTask(
        name="A", dependencies=[preprocess_task], duration=10, group_name="workers"
    )
    b_task = SleepTask(
        name="B", dependencies=[preprocess_task], duration=15, group_name="workers"
    )
    c_task = SleepTask(
        name="C", dependencies=[preprocess_task], duration=20, group_name="workers"
    )
    d_task = SleepTask(name="D", dependencies=[a_task], duration=7)

    post_process_task = SleepTask(
        name="post_process", dependencies=[a_task, b_task, c_task, d_task], duration=3
    )

    flow.register_tasks(
        preprocess_task,
        a_task,
        b_task,
        c_task,
        d_task,
        post_process_task,
    )

    logger.info("Graph iteration order:")
    for i, task in enumerate(flow.iter_graph(), start=1):
        logger.info(f"{i}. {task}")

    viz = FlowVisualizer(flow)

    logger.info("Running Flow")
    flow.run()
    viz.join()


if __name__ == "__main__":
    example_flow()
