qBittorrent Search plugins
==========================

[bakabt.me](https://bakabt.me) is a site that specialises in high-quality,
well-seeded and complete anime-related materials.

[linuxtracker](http://linuxtracker.org) is a tracker for linux torrents,
including distro .iso files and software tarballs.

[Nyaa.pantsu](https://nyaa.pantsu.cat) and [Nyaa.si](https://nyaa.si) are
drop-in replacements for the now removed NyaaTorrents.

Installation
------------

### Linuxtracker
Simply download the [plugin file](engines/linuxtracker.py) or copy the
following [link](https://github.com/MadeOfMagicAndWires/qBit-plugins/raw/master/engines/linuxtracker.py).

After you've done this you can add this plugin to qBittorrent by going:

<kbd>Search tab</kbd> 🡪 <kbd>Search Plugins</kbd> 🡪 <kbd>Install a new one</kbd>  
<kbd>Local File</kbd> then select the plugin file
 **or**
<kbd>Web Link</kbd> then insert the link you copied.

Or by manually copying the `bakabt.py` to the following location:
  * Linux: `~/.local/share/data/qBittorrent/nova/engines/linuxtracker.py`
  * Mac: ``~/Library/Application Support/qBittorrent/nova/engines/linuxtracker.py`
  * Windows: `C:\Documents and Settings\username\Local Settings\Application Data\qBittorrent\nova\engines\linuxtracker.py`

### Nyaas
Take [this](engines/nyaapantsu.py) or [this](engines/nyaasi.py) file and follow
the steps above. 

**Please note that Nyaa.pantsu is somewhat unstable and that it might not
work. The plugin works, you might just have to try it a few times.**

### BakaBT
Because BakaBT requires your login info, this plugin requires a bit more work than most.

1. Firstly you'll need an ~~[account](https://bakabt.me/signup.php)~~
   (Admission currently closed)
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
After this is done you can follow the same steps as with the other plugins.

F.A.Q
-----

1. **This plugin doesn't require my torrent pass, does this plugin provide personalized torrents?**

  Because the plugin logs you in for every search, this means that the torrent files you open using it are your
  personal ones. It's effectively no different than if you'd visit the site and download the torrent manually.


### License

All files are distributed under the GPL licence
