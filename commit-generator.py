#! /usr/bin/env python3
import pyperclip
import json
from pathlib import Path
import os
from colored import fg, attr


class Commit(object):

    def __init__(self) -> None:
        self.load_config()
        self.commit_type()
        self.commit_scope()
        self.commit_subject()
        self.commit_body()
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
            self.type = self.prompt("Type of change: ")
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
        print(fg("blue") + " ".join(lst) + attr("reset"))
        while True:
            self.scope = self.prompt("Scope: ").strip().split()
            for i in self.scope:
                if i not in lst:
                    print(fg("red") +
                          "Space separated multiple choice" + attr("reset"))
                    break
            else:
                break

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
        if self.body:
            if self.prompt("API change [y|n]: ", optional=True) == "y":
                self.breaking_change = self.form_lines(
                    self.prompt("Describe change: "))
            else:
                self.breaking_change = False
        elif self.breaking_change:
            self.breaking_change = self.form_lines(
                self.prompt("Describe API change: "))
        if self.type == "fix":
            while True:
                try:
                    self.fixes = self.prompt("Fixes issue no.: ", optional=True)
                    if self.fixes:
                        self.fixes = int(self.fixes)
                    break
                except:
                    print(fg("red") + "Must be a number" + attr("reset"))
        else:
            self.fixes = False

    def create_commit(self) -> None:
        lst = self.config["gitmojis"]
        for i in lst:
            if i["type"] == self.type:
                self.emoji = i["emoji"]
        commit = self.emoji + ' ' + self.type.lower()
        if self.scope:
            commit = commit + "(" + ", ".join(self.scope).lower() + ")"
        if self.breaking_change:
            commit = commit + "!"
        commit = commit + ": "
        commit = commit + self.subject.lower()
        if self.body:
            commit = commit + "\n\n" + self.body.lower()
        if self.breaking_change:
            commit = commit + "\n\nBREAKING CHANGE:\n\n" + self.breaking_change
        if self.fixes:
            commit = commit + f"\n\n\nFixes #{self.fixes}"
        self.commit = commit

    def to_clipboard(self) -> None:
        pyperclip.copy(self.commit)
        print("\n"+self.commit)
        print("\nCopied to clipboard")


if __name__ == "__main__":
    commit = Commit()
    commit.create_commit()
    commit.to_clipboard()
