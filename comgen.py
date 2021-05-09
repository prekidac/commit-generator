#! /usr/bin/env python3
import logging
from typing import ChainMap
import pyperclip
import json
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
        self.commit_footer()

    def load_config(self) -> None:
        with open("config.json", "r") as f:
            self.config = json.load(f)

    def all_types(self) -> dict:
        """type: description"""
        dct = {}
        for i in self.config["gitmojis"]:
            dct[i["type"]] = i["description"]
        return dct

    def all_scopes(self) -> list:
        return self.config["scopes"]

    def prompt(self, prompt: str, optional: bool = False) -> str:
        while True:
            i = input(prompt)
            if optional or i != "":
                return i

    def commit_type(self) -> None:
        dct = self.all_types()
        for key, value in dct.items():
            print(
                f"{fg('red')+attr('bold')+key+attr('reset')+fg('blue')+' - '+value+attr('reset')}")
        while True:
            self.type = self.prompt(f"Type of change: ")
            if self.type in dct.keys():
                break

    def commit_scope(self) -> None:
        lst = self.all_scopes()
        self.scope = self.prompt(
            f"{fg('blue')+' '.join(lst)+attr('reset')}\nScope: ", optional=True)
        if self.scope not in lst:
            self.scope = None

    def commit_subject(self) -> None:
        self.subject = self.prompt("Message (what): ")

    def commit_body(self) -> None:
        self.body = self.prompt("Description (why): ", optional=True)

    def commit_footer(self) -> None:
        if self.prompt("API change [y|n]: ", optional=True) == "y":
            self.breaking_change = self.prompt("Describe change: ")
        else:
            self.breaking_change = False

    def create_commit(self) -> None:
        lst = self.config["gitmojis"]
        for i in lst:
            if i["type"] == self.type:
                self.emoji = i["emoji"]
        commit = self.emoji + ' ' + self.type
        if self.scope:
            commit = commit + f"({self.scope}): "
        else:
            commit = commit + ": "
        commit = commit + self.subject.lower()
        if self.body:
            commit = commit + "\n\n" + self.body.capitalize()
        if self.breaking_change:
            commit = commit + "\n\nBREAKING CHANGE: " + self.breaking_change
        self.commit = commit

    def to_clipboard(self) -> None:
        pyperclip.copy(self.commit)
        print(self.commit)
        print("Copied to clipboard")


if __name__ == "__main__":
    commit = Commit()
    commit.create_commit()
    commit.to_clipboard()
