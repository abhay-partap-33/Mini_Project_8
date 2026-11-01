
import json
import os
from datetime import date

from models import (
    Book, Magazine, ReferenceBook,
    StudentMember, ResearchStudent,
    FacultyMember, NotifiedMember
)


def _item_to_dict(item):

    return {
        "item_type": type(item).__name__,
        "item_id": item.item_id,
        "title": item.title,
        "available": item.available
    }


def _member_to_dict(member):

    return {
        "member_type": type(member).__name__,
        "member_id": member.member_id,
        "name": member.name,
        "borrowing_limit": member.borrowing_limit
    }


def save_data(manager, file_path):

    data = {
        "items": [
            _item_to_dict(item)
            for item in manager.items.values()
        ],

        "members": [
            _member_to_dict(member)
            for member in manager.members.values()
        ],

        "loans": list(manager.loans.values())
    }

    temporary_path = f"{file_path}.tmp"

    with open(temporary_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    os.replace(temporary_path, file_path)


def load_data(manager, file_path):

    if not os.path.exists(file_path):
        return

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON data: {error}"
        ) from error

    if not isinstance(data, dict):
        raise ValueError("Data must be a JSON object.")

    for section in ("items", "members", "loans"):

        if section not in data or not isinstance(data[section], list):
            raise ValueError(f"Invalid {section} section.")

    item_classes = {
        "Book": Book,
        "Magazine": Magazine,
        "ReferenceBook": ReferenceBook
    }

    member_classes = {
        "StudentMember": StudentMember,
        "ResearchStudent": ResearchStudent,
        "FacultyMember": FacultyMember,
        "NotifiedMember": NotifiedMember
    }

    items = {}
    members = {}
    loans = {}

    # Restore items
    for record in data["items"]:

        if not isinstance(record, dict):
            raise ValueError("Invalid item record.")

        item_type = record.get("item_type")
        item_class = item_classes.get(item_type)

        item_id = record.get("item_id")
        title = record.get("title")
        available = record.get("available")

        if item_class is None:
            raise ValueError("Unknown item type.")

        if not isinstance(item_id, str) or not item_id.strip():
            raise ValueError("Invalid item ID.")

        if not isinstance(title, str) or not title.strip():
            raise ValueError("Invalid item title.")

        if not isinstance(available, bool):
            raise ValueError("Invalid availability value.")

        if item_id in items:
            raise ValueError("Duplicate item ID in JSON.")

        items[item_id] = item_class(
            item_id, title, available
        )

    # Restore members
    for record in data["members"]:

        if not isinstance(record, dict):
            raise ValueError("Invalid member record.")

        member_type = record.get("member_type")
        member_class = member_classes.get(member_type)

        member_id = record.get("member_id")
        name = record.get("name")
        limit = record.get("borrowing_limit")

        if member_class is None:
            raise ValueError("Unknown member type.")

        if not isinstance(member_id, str) or not member_id.strip():
            raise ValueError("Invalid member ID.")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Invalid member name.")

        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("Invalid borrowing limit.")

        if member_id in members:
            raise ValueError("Duplicate member ID in JSON.")

        members[member_id] = member_class(
            member_id, name, limit
        )

    # Restore active loans
    for record in data["loans"]:

        if not isinstance(record, dict):
            raise ValueError("Invalid loan record.")

        item_id = record.get("item_id")
        member_id = record.get("member_id")

        issue_date = record.get("issue_date")
        due_date = record.get("due_date")

        if item_id not in items or member_id not in members:
            raise ValueError("Loan refers to an unknown item or member.")

        if item_id in loans:
            raise ValueError("Duplicate active loan.")

        if not isinstance(issue_date, str) or not isinstance(due_date, str):
            raise ValueError("Invalid loan dates.")

        date.fromisoformat(issue_date)
        date.fromisoformat(due_date)

        loans[item_id] = {
            "item_id": item_id,
            "member_id": member_id,
            "issue_date": issue_date,
            "due_date": due_date
        }

    # Reconstruct availability and member borrowing counts
    for item in items.values():
        item.checkin()

    for member in members.values():
        member.clear_loans()

    for item_id, loan in loans.items():

        if not items[item_id].is_lendable:
            raise ValueError("A non-lendable item has an active loan.")

        items[item_id].checkout()

        members[loan["member_id"]].add_loan(item_id)

    manager.items = items
    manager.members = members
    manager.loans = loans
