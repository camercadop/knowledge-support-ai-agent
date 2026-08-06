import importlib
import pkgutil

for _info in pkgutil.iter_modules(__path__, __name__ + "."):
    if _info.name.split(".")[-1] not in ("registry",):
        importlib.import_module(_info.name)
