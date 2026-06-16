from __future__ import annotations
from typing import Iterator, Type, TypeVar
from engine.ecs.component import Component

T = TypeVar("T", bound=Component)


class EntityError(Exception):
    pass


class World:
    """Owns entities and their components and runs the registered systems.

    Components are stored per type so a query over one type stays cheap.
    Entity ids are never reused inside a single run, which keeps stale
    references detectable instead of silently aliasing a new entity.
    """

    def __init__(self) -> None:
        self._next_id: int = 1
        self._alive: set[int] = set()
        self._components: dict[Type[Component], dict[int, Component]] = {}
        self._destroy_queue: list[int] = []
        self._resources: dict[str, object] = {}

    def CreateEntity(self) -> int:
        entity = self._next_id
        self._next_id += 1
        self._alive.add(entity)
        return entity

    def IsAlive(self, entity: int) -> bool:
        return entity in self._alive

    def DestroyEntity(self, entity: int) -> None:
        if entity not in self._alive:
            return

        self._destroy_queue.append(entity)

    def FlushDestroyed(self) -> None:
        for entity in self._destroy_queue:
            self._RemoveEntityNow(entity)

        self._destroy_queue.clear()

    def _RemoveEntityNow(self, entity: int) -> None:
        self._alive.discard(entity)

        for store in self._components.values():
            store.pop(entity, None)

    def AddComponent(self, entity: int, component: Component) -> Component:
        if entity not in self._alive:
            raise EntityError(f"cannot add component to dead entity {entity}")

        store = self._components.setdefault(type(component), {})
        store[entity] = component
        return component

    def RemoveComponent(self, entity: int, component_type: Type[Component]) -> None:
        store = self._components.get(component_type)

        if store is not None:
            store.pop(entity, None)

    def HasComponent(self, entity: int, component_type: Type[Component]) -> bool:
        store = self._components.get(component_type)
        return store is not None and entity in store

    def GetComponent(self, entity: int, component_type: Type[T]) -> T:
        store = self._components.get(component_type)

        if store is None or entity not in store:
            raise EntityError(f"entity {entity} has no {component_type.__name__}")

        return store[entity]  # type: ignore[return-value]

    def TryGetComponent(self, entity: int, component_type: Type[T]) -> T | None:
        store = self._components.get(component_type)

        if store is None:
            return None

        return store.get(entity)  # type: ignore[return-value]

    def GetEntitiesWith(self, *component_types: Type[Component]) -> Iterator[int]:
        if not component_types:
            return iter(())

        stores = [self._components.get(ct, {}) for ct in component_types]
        smallest = min(stores, key=len)

        for entity in list(smallest.keys()):
            if all(entity in store for store in stores):
                yield entity

    def SetResource(self, key: str, value: object) -> None:
        self._resources[key] = value

    def GetResource(self, key: str) -> object:
        if key not in self._resources:
            raise EntityError(f"no world resource named '{key}'")

        return self._resources[key]

    def CountEntities(self) -> int:
        return len(self._alive)
