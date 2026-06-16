from __future__ import annotations


class Component:
    """Marker base for all ECS components. A component holds data, never behaviour."""

    def __str__(self) -> str:
        fields = ", ".join(f"{key}={value}" for key, value in vars(self).items())
        return f"{type(self).__name__}({fields})"
