#! /usr/bin/env python3
import logging
from typing import ChainMap
import pyperclip
import json
from pathlib import Path
import os
from colored import fg, attr

FORMAT = "%(filename)s: %(levelname)s: %(message)s: line: %(lineno)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

# logging.disable(logging.WARNING)


class Commit(object):

    def __init__(self) -> None:
        self.load_config()
        self.commit_type()
        self.commit_scope()
        self.commit_subject()
        self.commit_body()
        if self.breaking_change or self.body:
            self.commit_footer()

    def load_config(self) -> None:
        config = os.path.join(Path.home(), ".local/share/commit-config.json")
        with open(config, "r") as f:
            self.config = json.load(f)

    def all_types(self) -> list:
        lst = []
        for i in self.config["gitmojis"]:
            lst.append(i["type"])
        return lst

    def prompt(self, prompt: str, optional: bool = False) -> str:
        while True:
            i = input(prompt).rstrip(".")
            if optional or i != "":
                return i

    def commit_type(self) -> None:
        lst = self.all_types()
        while True:
            self.type = self.prompt(f"Type of change: ")
            if self.type.rstrip("!") in lst:
                if self.type[-1] == "!":
                    self.breaking_change = True
                    self.type = self.type.rstrip("!")
                else:
                    self.breaking_change = False
                break
            print(fg('blue')+" ".join(lst)+attr('reset'))

    def commit_scope(self) -> None:
        lst = self.config["scopes"]
        self.scope = self.prompt(
            f"{fg('blue')+' '.join(lst)+attr('reset')}\nScope: ", optional=True)
        if self.scope not in lst:
            self.scope = None

    def commit_subject(self) -> None:
        max_length = int(self.config["subject_length"])
        while True:
            self.subject = self.prompt("Message (what): ")
            if len(self.subject) <= max_length:
                break
            print(self.subject[0:max_length] + fg("red") +
                  self.subject[max_length:]+attr("reset"))
            print(
                fg('red') + f"Max. subject length {max_length} characters" + attr("reset"))

    def commit_body(self) -> None:
        self.body = self.form_lines(self.prompt(
            "Description (why): ", optional=True))

    def form_lines(self, raw: str) -> str:
        max_length = int(self.config["max_body_line_length"])
        lst = raw.strip().split()
        out = []
        line = ""
        for i in lst:
            if len(line) == 0:
                line = i
                continue
            if len(line+i) < max_length:
                line = line + " " + i
            else:
                out.append(line)
                line = i
        else:
            out.append(line)
        return "\n".join(out)

    def commit_footer(self) -> None:
        if self.prompt("API change [y|n]: ", optional=True) == "y":
            self.breaking_change = self.form_lines(
                self.prompt("Describe change: "))
        else:
            self.breaking_change = False

    def create_commit(self) -> None:
        lst = self.config["gitmojis"]
        for i in lst:
            if i["type"] == self.type:
                self.emoji = i["emoji"]
        commit = self.emoji + ' ' + self.type.lower()
        if self.scope:
            commit = commit + f"({self.scope.lower()}): "
        else:
            commit = commit + ": "
        commit = commit + self.subject.lower()
        if self.body:
            commit = commit + "\n\n" + self.body.capitalize()
        if self.breaking_change:
            commit = commit + "\n\nBREAKING CHANGE:\n\n" + self.breaking_change
        self.commit = commit

    def to_clipboard(self) -> None:
        pyperclip.copy(self.commit)
        print("\n"+self.commit)
        print("\nCopied to clipboard")


if __name__ == "__main__":
    commit = Commit()
    commit.create_commit()
    commit.to_clipboard()
