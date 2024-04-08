from threading import Timer
from ortools.sat.python import cp_model

class intermediateSolutionHandler(cp_model.CpSolverSolutionCallback):
    def __init__(self, limit: int, early_stopping_timeout:int = 0):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__solution_count = 0
        self.__solution_limit = limit
        self.early_stopping_timeout = early_stopping_timeout
        self.timer = None

    def on_solution_callback(self) -> None:
        self.__solution_count += 1
        value = self.ObjectiveValue()
        time = self.WallTime()
        print(f"new solution: {value} in {time}s")
        if self.__solution_limit != 0 and self.__solution_count >= self.__solution_limit:
            print(f"Stop search after {self.__solution_limit} solutions")
            self.stop_search()
        if self.timer:
                self.timer.cancel()
        if(self.early_stopping_timeout > 0):
            self.timer = Timer(self.early_stopping_timeout, self.stop)
            self.timer.start()

    def stop(self):
        print(f'stopping search since no solution has been found for {self.early_stopping_timeout}s. {self.solution_count} intermediary solutions')
        self.stop_search()

    def clean(self):
        "Clean up timer"
        if self.timer:
            self.timer.cancel()

    @property
    def solution_count(self) -> int:
        return self.__solution_count
    