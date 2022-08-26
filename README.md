# TPLN

A simple task manager/runner for your Python projects.

## Description

This tool takes the basic principle behind tools like [Airflow](https://github.com/apache/airflow) or [Luigi](https://github.com/spotify/luigi) and makes it accesible to use **inside** your application.

Often times software is created to process data by tranforming it in multiple step, sometimes relying on external tools as part of the process. In these cases, it is sometimes better to think of your program as a flow, orchestrating multiple *tasks* each responsible for part of the process. Each of these tasks has a set of dependencies, and once complete your flow can be represented as a directed acyclic graph (or DAG). By traversing this DAG, you can then easily run your tasks in the required order, and tasks that don't depend on each other can even be parallelized.

However, the tooling available to accomplish this task seamed very heavyweight. Many assumptions are made, such as:
- The developper is root on the machine the software will be running on
- Each task is a fully-fledged program
- The flow is defined once, and then reused multiple times

I've found these assumptions to often be incorrect, and found myself needing a library that I could embed in my Python scripts to manage the following cases:
- Neither the user or I is root
- The flow is dynamically generated based on user input and can vary wildly between two different runs
- The flow is made up of both Python functions and external programs, and I don't want to spawn extra Python interpreters just to run individual functions as standalone processes.

THIS IS NOT A STANDALONE APPLICATION. If you're looking to replace Cron or something, TPLN is not the tool for you. Try Luigi, it looks cool. TPLN is designed to be **embedded inside other programs**, and to be as **minimal** as possible so as to not have any significant performance hit in of itself.

## Getting Started

### Dependencies

* python ^3.10 (Probably not needed, 3.7 should be fine but I haven't tested it)
* networkx ^2.8.5
* matplotlib ^3.5.3
* pygraphviz ^1.10
* asyncio ^3.4.3

### Installing

Three options are available to you:
1. Install it using pip: `pip install tpln`
2. Add it as a dependency in your Poetry project: `poetry add tpln`
3. Download the library source code, and include it into your codebase somewhere accessible through your PYTHONPATH. You'll have to do the same with any dependencies, and I won't be able to provide support for this as there are too many platform-specific issues to deal with.

## Version History

* 0.1.0
    * Initial Release

## License

This project is licensed under the MIT License - see the LICENSE.md file for details
