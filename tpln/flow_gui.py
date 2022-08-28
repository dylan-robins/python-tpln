#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8
# *****************************************************************************#
from __future__ import annotations

import tkinter as tk
from multiprocessing import Process, Queue
from queue import Empty
from tkinter import ttk

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from networkx.drawing.nx_agraph import graphviz_layout

from .flow import Flow
from .tasks import Task, TaskState


class DAG_GUI(tk.Tk):
    cmap = {
        TaskState.pending: "gray",
        TaskState.running: "skyblue",
        TaskState.done: "limegreen",
    }

    def __init__(
        self, initial_tasks: set[Task], queue: Queue, title: str = "DAG GUI example"
    ):
        super().__init__()

        self.queue = queue
        self.flow = Flow()
        self.flow.register_tasks(*initial_tasks)
        self.pos = graphviz_layout(self.flow.graph, prog="dot")

        self.protocol("WM_DELETE_WINDOW", self.handle_exit)

        self.title_label = ttk.Label(master=self, text=title)
        self.title_label.pack()

        self.figure = plt.figure(figsize=(6, 5), dpi=100)
        self.ax = self.figure.gca()
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(expand=True, fill="both")
        # toolbar.get_tk_widget().pack(expand=True, fill="both")

        self.draw_dag()

    def handle_exit(self):
        self.quit()
        self.destroy()

    def draw_dag(self):
        self.ax.clear()
        node_name_mapping = {task.id: task.name for task in self.flow.tasks}
        node_color_mapping = [
            self.cmap[self.flow.get_task_by_id(node).state] for node in self.flow.graph
        ]
        nx.draw(
            self.flow.graph,
            node_size=700,
            with_labels=True,
            labels=node_name_mapping,
            node_color=node_color_mapping,
            pos=self.pos,
            ax=self.ax,
        )
        self.canvas.draw()

        try:
            task_id, new_state = self.queue.get(timeout=0.1)
            self.flow.get_task_by_id(task_id).state = new_state
        except Empty:
            pass

        self.after(100, self.draw_dag)


class FlowVisualizer(Process):
    def __init__(self, flow: Flow):
        super().__init__()

        self.queue = flow.gui_msg_queue
        self.tasks = flow.tasks
        self.start()

    def run(self):
        app = DAG_GUI(self.tasks, self.queue)
        app.mainloop()
