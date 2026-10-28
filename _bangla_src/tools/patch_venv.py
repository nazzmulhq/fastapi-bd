"""Make griffe-typingdoc (used by the FastAPI docs config) tolerant of annotations it does not expect.

The Pydantic AI sources contain `Generator[X | Y]` (one type argument) and `**kwargs: Unpack[SomeTypedDict]` whose
TypedDict lives in a package that is not available to the docs build; griffe-typingdoc crashes the whole build on
both. This idempotently patches the installed copy in the build venv (run by build_bn.py before building).
"""
import os
import griffe_typingdoc
p = os.path.join(os.path.dirname(griffe_typingdoc.__file__), '_internal', 'static.py')
s = open(p, encoding='utf8').read()
orig = s
PATCHES = [
    ('yield_annotation = annotation.slice.elements[0]  # ty:ignore[unresolved-attribute]',
     "yield_annotation = getattr(annotation.slice, 'elements', [annotation.slice])[0]  # bn-patch"),
    ('receive_annotation = annotation.slice.elements[1]  # ty:ignore[unresolved-attribute]',
     "receive_annotation = (list(getattr(annotation.slice, 'elements', [])) + [None, None])[1]  # bn-patch"),
    ('return_annotation = annotation.slice.elements[2]  # ty:ignore[unresolved-attribute]',
     "return_annotation = (list(getattr(annotation.slice, 'elements', [])) + [None, None, None])[2]  # bn-patch"),
    ('                typed_dict = func.modules_collection[slice_path]\n                params_data',
     '                try:  # bn-patch\n                    typed_dict = func.modules_collection[slice_path]\n'
     '                except Exception:  # bn-patch\n                    break\n                params_data'),
]
for old, new in PATCHES:
    if old in s:
        s = s.replace(old, new)
if s != orig:
    open(p, 'w', encoding='utf8').write(s)
    print('patched', p)
else:
    print('nothing to patch', p)
