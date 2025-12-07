# escaper/core/room.py
"""Room and object models for escape room scenarios."""

from dataclasses import dataclass
from typing import List, Dict, Optional
import json


@dataclass
class Lock:
    """Represents a lock on an object that requires a password."""
    password: str
    password_type: str          # "code" | "word" | "pattern"
    on_success_text: str
    on_failure_text: str
    reveal_objects: List[str]
    escape: bool


@dataclass
class RoomObject:
    """Represents an object in the escape room."""
    id: str
    name: str
    category: str               # "door" | "clue" | "container" | "decor" | "other"
    visible: bool
    inspect_text: Optional[str]
    lock: Optional[Lock]


@dataclass
class Room:
    """Represents an escape room scenario."""
    room_id: str
    title: str
    intro: str
    objects: Dict[str, RoomObject]
    escaped: bool = False

    @classmethod
    def from_json(cls, path: str) -> "Room":
        """Load a room from a JSON file."""
        with open(path, "r") as f:
            data = json.load(f)
        
        objs = {}
        for obj in data["objects"]:
            lock = None
            if obj.get("lock") is not None:
                l = obj["lock"]
                lock = Lock(
                    password=l["password"],
                    password_type=l["password_type"],
                    on_success_text=l["on_success_text"],
                    on_failure_text=l["on_failure_text"],
                    reveal_objects=l.get("reveal_objects", []),
                    escape=l.get("escape", False),
                )
            objs[obj["id"]] = RoomObject(
                id=obj["id"],
                name=obj["name"],
                category=obj["category"],
                visible=obj["visible"],
                inspect_text=obj.get("inspect_text"),
                lock=lock
            )
        
        return cls(
            room_id=data["room_id"],
            title=data["title"],
            intro=data["intro"],
            objects=objs
        )

    def visible_objects(self) -> List[RoomObject]:
        """Return list of currently visible objects."""
        return [o for o in self.objects.values() if o.visible]

    def inspect_object(self, object_id: str) -> str:
        """Inspect an object and return its description."""
        obj = self.objects.get(object_id)
        if obj is None:
            return f"There is no object with id '{object_id}'."
        if obj.inspect_text:
            return obj.inspect_text
        return f"You inspect the {obj.name}, but find nothing special."

    def try_password(self, object_id: str, password: str) -> str:
        """Try a password on a locked object."""
        obj = self.objects.get(object_id)
        if obj is None:
            return f"There is no object with id '{object_id}'."
        if obj.lock is None:
            return f"The {obj.name} does not seem to have any password lock."
        
        if password == obj.lock.password:
            # Success
            # Reveal hidden objects
            for oid in obj.lock.reveal_objects:
                if oid in self.objects:
                    self.objects[oid].visible = True
            if obj.lock.escape:
                self.escaped = True
            return obj.lock.on_success_text
        else:
            # Failure
            return obj.lock.on_failure_text

