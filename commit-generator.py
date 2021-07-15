#! /usr/bin/env python3
import pyperclip
import json
from pathlib import Path
import os
import questionary
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
        self.override_config()

    def override_config(self) -> None:
        try:
            with open("commit-config.json", "r") as f:
                self.config.update(json.load(f))
        except:
            pass

    def all_types(self) -> list:
        lst = []
        for i in self.config["gitmojis"]:
            lst.append(i["type"])
        return lst

    def commit_type(self) -> None:
        lst = self.all_types()
        self.type = questionary.select(
            "Type of change",
            lst).ask()
        if self.type == None:
            exit(1)

    def commit_scope(self) -> None:
        lst = self.config["scopes"]
        self.scope = questionary.checkbox(
            "Scope",
            lst,
            validate=lambda x: "Pick one or more" if not x else True).ask()
        if self.scope == None:
            exit(1)

    def commit_subject(self) -> None:
        max_length = int(self.config["subject_length"])
        self.subject = questionary.text(
            "Message (what):",
            validate=lambda x: f"Subject length 5 - {max_length} characters"
            if len(x) > max_length or len(x) < 5 else True).ask()
        if self.subject == None:
            exit(1)

    def commit_body(self) -> None:
        body = questionary.text("Description (why):").ask()
        if body == None:
            exit(1)
        else:
            self.body = self.form_lines(body)

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
        if self.type == "change" and questionary.confirm(
            "API change:",
            default=False).ask():
            self.breaking_change = self.form_lines(
                questionary.text(
                    "API change (before => after):",
                    validate=lambda x: "Type" if len(x) < 5 else True).unsafe_ask())
        else:
            self.breaking_change = False

        def check(x) -> None:
            try:
                if not x or int(x):
                    return True
            except:
                return "Number or none"
        if self.type == "fix":
            self.fixes = questionary.text(
                "Fixes issue no.:",
                validate=check).ask()
        else:
            self.fixes = False

    def create_commit(self) -> None:
        lst = self.config["gitmojis"]
        for i in lst:
            if i["type"] == self.type:
                self.emoji = i["emoji"]
        commit = self.emoji + " " + self.type.lower()
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
            commit = commit + f"\n\nFixes #{self.fixes}"
        self.commit = commit

    def to_clipboard(self) -> None:
        pyperclip.copy(self.commit)
        print(fg(8)+"-"*15+attr("reset"))
        print("\n"+self.commit+"\n")
        print(fg(8)+"-"*15+attr("reset"))
        print(fg(3)+"Copied to clipboard"+attr("reset"))


if __name__ == "__main__":
    commit = Commit()
    commit.create_commit()
    commit.to_clipboard()
