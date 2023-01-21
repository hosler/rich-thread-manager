from rich.console import Console
from rich.console import Group
from rich.panel import Panel
from rich import print
from rich.layout import Layout
import logging
from rtm.logging.handlers import PopBufferingHandler
import random
import time
import queue, threading
from queue import Empty

from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.pretty import Pretty
from rich.prompt import Prompt

# Set up the main/root logger
main_logger = logging.getLogger()
main_logger.setLevel(logging.DEBUG)

# Instantiate the buffering handler we will watch from within Rich
buffering_handler = PopBufferingHandler(capacity=2000)
main_logger.addHandler(buffering_handler)

# Local logger
log = logging.getLogger("rich")


class DumbThread(threading.Thread):
    def __init__(self, id, logger, queue):
        threading.Thread.__init__(self)
        self.id = id
        self.queue = queue
        self.logger = logger

    def run(self):
        while True:
            try:
                sub = self.queue.get(timeout=5)
            except Empty:
                break
            time.sleep(5)
            self.logger.info(f'THREAD {self.id}: {sub}')
            self.queue.task_done()





def get_log(max_height) -> Table:
    buffering_handler.capacity = max_height - 3
    table = Table(show_header=False, pad_edge=False, show_edge=False)
    for row in buffering_handler.buffer:
        table.add_row(f'{row.msg}')
    return table

def generate_layout(console, threads, progress) -> Layout:
    layout = Layout()
    render_map = layout.render(console, console.options)
    text = Text()
    layout.split_column(
        Layout(name="top", ratio=9),
        Layout(Panel(progress,title="Overall Progress",
        border_style="green",
        padding=(2, 2),), name="bottom"),
    )
    layout["top"].split_row(
        Layout(Panel(get_log(render_map[layout].region.height)), name="left", ratio=4),
        Layout(Panel(generate_table(threads)), name="right"),
    )
    return layout


def generate_table(threads) -> Table:
    table = Table(show_header=False, pad_edge=False, show_edge=False)
    for thread in threads:
        table.add_row(
            f"{thread.id}", "[green]RUNNING" if thread.is_alive() else "[red]STOPPED"
        )
    return table

queue = queue.Queue()

for counter in range(40):
    queue.put(counter)

total = queue.qsize()

threads = []

for i in range(10):
    ft = DumbThread(i, log, queue)
    ft.start()
    threads.append(ft)


# #layout["upper"].split_column(generate_table())
# print(layout)

console = Console()
from rich.progress import Progress


progress = Progress()

with Live(generate_layout(console, threads, progress), refresh_per_second=4, console=console) as live:
    ts = threading.enumerate()
    task = progress.add_task("All Jobs", total=int(total))
    while any(thread.is_alive() for thread in threads):
        time.sleep(0.4)
        live.update(generate_layout(console, threads, progress))
        completed = total - queue.unfinished_tasks
        progress.update(task, completed=completed)

for thread in threads:
    thread.join()