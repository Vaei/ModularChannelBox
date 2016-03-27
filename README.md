# ModularChannelBox

* [Google Doc Instructions available here] (https://docs.google.com/document/d/18gK96SybUZo6IQchlnH-d15BKcKONmJVAci0nI8jBtY/edit?usp=sharing)

All Users
---------

* Re-order or remove options from channel box menus
* Change settings not available in the default menu
   - Hide popup menu labels
   - Hide unavailable menu items instead of disabling them
   - Remove symbol buttons from the upper-right of the ChannelBox
* Store your settings between restarts
   - Precision
   - Names
   - And more
* Add custom menus and switch between them on the fly using the drop-down box in the provided UI

Developer Use
----------

* Specialized ChannelBox for your own UIs
    Maya's channel box menu only exists in the primary channel box and has no customization or modularity.
* Add, remove, or modify functions
* Add option boxes to existing items for alternate behaviour
* Add your own script job functions
* Save data to be restored later and optionally serialize the data to disk to use between restarts


Primary Differences
-----------
* Settings that maintain their state will not reset when closing or re-opening Maya
* "Show" menu has been redesigned, feedback is welcomed - the original show menu was prone to error and subjectively impractical for use
* OptionBox added in Freeze Submenu to create a helpful dialog, try it out
* Assets / Containers are ommitted, there would have to be a lot of demand for this to change
* Extra tooltips added
