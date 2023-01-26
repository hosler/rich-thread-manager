from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.progress import Progress

from readchar import readkey, key

import time, logging, queue, threading
from queue import Empty

from rtmui.loghandlers import PopBufferingHandler

class ThreadManager(threading.Thread):
    def press(self, key):
        if key == "=":
            ft = self.thread_class(len(self.threads)+1, self.logger, self.queue)
            ft.start()
            self.threads.append(ft)
        if key == "-":
            ft = self.threads.pop()
            ft.kill()

    def __init__(self, logger, threads, queue, thread_class):
        threading.Thread.__init__(self, daemon=True)
        self.logger = logger
        self.threads = threads
        self.queue = queue
        self.thread_class = thread_class
        self.logger.info("Manager started")

    def run(self):
        while True:
            k = readkey()
            if k == "=":
                ft = self.thread_class(len(self.threads) + 1, self.logger, self.queue)
                ft.start()
                self.threads.append(ft)
            if k == "-":
                ft = self.threads.pop()
                ft.kill()
            time.sleep(.5)


class Manager:
    def get_log(self, max_height=200) -> Table:
        self.buffering_handler.capacity = max_height - 1
        table = Table(show_header=False, pad_edge=False, show_edge=False)
        for row in self.buffering_handler.buffer:
            table.add_row(f'{row.msg}')
        return table

    def generate_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="top", ratio=9),
            Layout(name="bottom", minimum_size=3)
        )
        layout["top"].split_row(
            Layout(name="left", ratio=4),
            Layout(name="right"),
        )
        return layout


    def generate_table(self) -> Table:
        table = Table(show_header=False, pad_edge=False, show_edge=False)
        for thread in self.threads:
            table.add_row(
                f"{thread.id}", "[green]RUNNING" if thread.is_alive() else "[red]STOPPED"
            )
        return table

    def __init__(self, logger, queue, thread_class):
        self.logger = logger
        self.rtm_logger = logging.getLogger("rtmui")
        self.rtm_logger.setLevel(logging.DEBUG)
        self.buffering_handler = PopBufferingHandler(capacity=2000)
        self.rtm_logger.addHandler(self.buffering_handler)
        self.queue = queue
        self.console = Console()
        self.threads = []
        self.thread_class = thread_class

    def run(self):
        total = self.queue.qsize()
        thread_manager = ThreadManager(
            logger=self.rtm_logger,
            threads=self.threads,
            queue=self.queue,
            thread_class=self.thread_class)
        thread_manager.start()

        layout = self.generate_layout()
        layout["top"]["left"].update(Panel(self.get_log()))
        layout["top"]["right"].update(Panel(self.generate_table()))
        progress = Progress()
        layout["bottom"].update(Panel(progress))
        task = progress.add_task("All Jobs", total=int(total))

        with Live(layout, refresh_per_second=4, console=self.console, screen=True) as live:
            while not self.queue.empty() or any(thread.is_alive() for thread in self.threads):
                render_map = layout.render(live.console, live.console.options)
                layout["top"]["left"].update(Panel(self.get_log(render_map[layout["top"]["left"]].region.height)))
                layout["top"]["right"].update(Panel(self.generate_table()))
                progress.update(task, completed=total-self.queue.unfinished_tasks)
                time.sleep(1)


        for thread in self.threads:
            thread.join()