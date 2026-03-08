# application/use_cases

Use cases represent individual user intents. Each use case is a class with a single public
`execute()` method. They orchestrate domain objects and outbound ports to fulfil one
specific operation.

## Files

| File | Class | Intent |
|---|---|---|
| `get_item_use_case.py` | `GetItemUseCase` | Fetch a single item by its ID |

## GetItemUseCase

```python
class GetItemUseCase:
    def __init__(self, item_repository: ItemRepository): ...

    @log_execution("use_cases")
    async def execute(
        self,
        item_id: int,
        query_params: QueryParams | None = None,
    ) -> ItemResponseDTO: ...
```

**Behaviour:**
1. Calls `item_repository.get_by_id(item_id)`.
2. Raises `ItemNotFoundError(item_id=item_id)` if the result is `None`.
3. Maps `Item` → `ItemResponseDTO` and returns.

The `@log_execution("use_cases")` decorator records entry, exit, and any errors without
adding noise to the use-case logic itself.

## Conventions for new use cases

- One class per file, named `<Verb><Noun>UseCase`.
- Constructor accepts only port abstractions (`from ports/`), never concrete adapters.
- Return a DTO from `application/dto/`; never return raw domain entities to callers.
- Raise domain errors from `domain/errors/` for expected failure conditions.
- Register a factory in `infrastructure/di/dependencies.py`.
- Inject in the router with `Annotated[MyUseCase, Depends(get_my_use_case)]`.

See `../README.md` for the full application layer overview.
