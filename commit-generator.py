#! /usr/bin/env python3
import pyperclip
import json
from pathlib import Path
import os
from questionary import Style
import questionary
from color_schema import questionary_style

style = Style(questionary_style)


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

    def commit_type(self) -> None:
        lst = self.all_types()
        self.type = questionary.select(
            "Type of change",
            lst,
            style=style).unsafe_ask()

    def commit_scope(self) -> None:
        lst = self.config["scopes"]
        self.scope = questionary.checkbox(
            "Scope",
            lst,
            style=style,
            validate=lambda x: "Pick one or more" if not x else True).unsafe_ask()

    def commit_subject(self) -> None:
        max_length = int(self.config["subject_length"])
        self.subject = questionary.text(
            "Message (what):",
            style=style,
            validate=lambda x: f"Subject length 5 - {max_length} characters"
            if len(x) > max_length or len(x) < 5 else True).unsafe_ask()

    def commit_body(self) -> None:
        self.body = self.form_lines(
            questionary.text(
                "Description (why):",
                style=style).unsafe_ask())

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
        if questionary.confirm(
            "API change:",
            default=False,
                style=style).ask():
            self.breaking_change = self.form_lines(
                questionary.text(
                    "Describe API change:",
                    style=style,
                    validate=lambda x: "Type" if len(x) < 5 else True).unsafe_ask())
        else:
            self.breaking_change = False
        if self.type == "fix":
            self.fixes = questionary.text(
                "Fixes issue no.:",
                style=style,
                validate=lambda x: "Number" if x and type(x) != int else True).unsafe_ask()
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
        questionary.print("-"*15, style=questionary_style[0][1])
        print("\n"+self.commit+"\n")
        questionary.print("-"*15, style=questionary_style[0][1])
        questionary.print(
            "Copied to clipboard",
            style="#FF9D00")


if __name__ == "__main__":
    commit = Commit()
    commit.create_commit()
    commit.to_clipboard()
