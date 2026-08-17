# CreateNew

adding/removing entries to the "New" menu


Calls several reg files to either add or remove keys, all reg files are shown below.


## Scripts

The following extensions have scripts to add/remove from context menu.

| accdb   |   |
|---|---|
| ahk  |   |
| bash |  |
| cmd |  |
| cpp |  |
| csv |  |

17 in total


Run the "" script to set up your new menu the way I like mine 

**Registry keys will be added and removed with admin privileges**

#### Removed items

#### Added items


---




---
### Notes

```batch
reg query "HKEY_CURRENT_USER\Software\Autodesk\AutoCAD\R18.0\ACAD-8001:409\Profiles\STDPROFILE" /s > toDelete.txt
for /f %v in (toDelete.txt) do reg delete %v
```

#### Script template

```batch
reg query "HKEY_CURRENT_USER\Software\Autodesk\AutoCAD\R18.0\ACAD-8001:409\Profiles\STDPROFILE" /s > toDelete.txt
for /f %v in (toDelete.txt) do reg delete %v
```

HKEY_CLASSES_ROOT
reg delete commands goes into .cmd file 

"[-]" goes into reg file

reg delete "HKEY_CLASSES_ROOT\.accdb\Access.Application.16\ShellNew"
[-HKEY_CLASSES_ROOT\.accdb\Access.Application.16\ShellNew]

reg delete "HKEY_CLASSES_ROOT\.bmp\shellex"
[-HKEY_CLASSES_ROOT\.bmp\shellex]

reg delete "HKEY_CLASSES_ROOT\.gdoc\ShellNew"
[-HKEY_CLASSES_ROOT\.gdoc\ShellNew]

reg delete "HKEY_CLASSES_ROOT\.gsheet\ShellNew"
[-HKEY_CLASSES_ROOT\.gsheet\ShellNew]

reg delete "HKEY_CLASSES_ROOT\.gslides\ShellNew"
[-HKEY_CLASSES_ROOT\.gslides\ShellNew]
---