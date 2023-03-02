from enum import Enum


class StateLogger:

    def __init__(self, name: str, states_representations: dict[Enum, str]):
        self.name = name
        self.displayed_once: bool = False
        self.previous_state = None
        self.current_state = None
        self.states_reprs: dict[Enum, str] = states_representations

    def update_state(self, state):
        if self.previous_state != self.current_state:
            self.previous_state = self.current_state
            self.displayed_once = False

        self.current_state = state

    def display_state(self):
        if not self.displayed_once:
            print(f"[{self.name} - {self.current_state}] {self.states_reprs[self.current_state]}")
            self.displayed_once = True
