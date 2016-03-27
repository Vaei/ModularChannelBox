# ModularChannelBox

* [Google Doc Instructions available here] (https://docs.google.com/document/d/18gK96SybUZo6IQchlnH-d15BKcKONmJVAci0nI8jBtY/edit?usp=sharing)

All Users
---------

Re-order or remove options from channel box menus, change settings not available in the default menu (popup menu label, hiding instead of disabling unavailable items, removing symbol buttons), or simply to have it store your settings between restarts. You can also add custom menus and switch between them on the fly using the drop-down box in the provided UI.

Developer Use
----------

Make a specialized channel box for your UIs, as Maya's channel box menu only exists in the primary channel box and has no customization or modularity.

Developers can add, remove, or modify functions. You can add option boxes to existing items, add script jobs, save data to be restored later and optionally serialize that data to disk to use between restarts.


Primary Differences
-----------
- Settings that maintain their state will not reset when closing or re-opening Maya
- "Show" menu has been redesigned, feedback is welcomed - the original show menu was prone to error and subjectively impractical for use
- OptionBox added in Freeze Submenu to create a helpful dialog, try it out
- Assets / Containers are ommitted, there would have to be a lot of demand for this to change
- Extra tooltips added
