class Thread:
  name =  ...  # type: str
class Lock:
  def __enter__(self) -> bool: ...
  def __exit__(self, *args): ...
class RLock: ...
def current_thread() -> Thread: ...