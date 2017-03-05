qBittorrent BakaBT searchplugin
===============================

[bakabt.me](https://bakabt.me) is a site that specialises in high-quality,well-seeded and complete anime-related materials.  
This plugin allows you to search BakaBT from within the qBittorrent integrated search.

Installation
------------
Because BakaBT requires your login info, this plugin requires a bit more work than most.

1. Firstly you'll need an [account](https://bakabt.me/signup.php)
2. Then you need to put your login information directly into the [plugin file](engines/bakabt.py):

You can do this by editing these specific lines (lineno. 52:53).
```python
    # Login information ######################################################
    #
    # SET THESE VALUES!!
    #
    username = "username"
    password = "password"
    ##########################################################################
    ...
```
Now replace the "username" and "password" with *your* username and password, surrounded by quotation marks.  
So if your username is `foobar` and your `password` is bazqux these lines should read:
```python
    ...
    # SET THESE VALUES
    #
    username = "foobar"
    password = "bazqux"
    ...
```

After you've done this you can add this plugin to qBittorrent by going:  
 <kbd>Search tab</kbd> 🡪 <kbd>Search Plugins</kbd> 🡪 <kbd>Install a new one</kbd> 🡪 Selecting the `bakabt.py` file.

Or by manually copying the `bakabt.py` to the following location:
  * Linux: `~/.local/share/data/qBittorrent/nova/engines/bakabt.py`
  * Mac: ``~/Library/Application Support/qBittorrent/nova/engines/bakabt.py`
  * Windows: `C:\Documents and Settings\username\Local Settings\Application Data\qBittorrent\nova\engines\bakabt.py`

F.A.Q
-----

1. **BakaBT is a public tracker. Why does this plugin need my login information?**

  Although the tracker is public, and anyone can download torrent files without an account,
  the [search functions](https://bakabt.me/browse.php) are only available to users.

2. **This plugin doesn't require my torrent pass, does this plugin provide personalized torrents?**

  Because the plugin logs you in for every search, this means that the torrent files you open using it are your
  personal ones. It's effectively no different than if you'd visit the site and download the torrent manually.

![](https://bakabt.me/resources/img/bg_1920.png)
