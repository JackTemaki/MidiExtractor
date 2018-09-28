# MidiExtractor

This tool reads meta events from midi files and saves all information for all tracks in a database.
This database information can then be used to extract midi tracks given a list of conditions, e.g. only guitar tracks.

Installation
------------

MidiExtractor requires the python3 version of python-midi:

 `pip3 install git+https://github.com/vishnubob/python-midi@feature/python3`
 
Usage
-----

Before extracting midi tracks create a database file that contains all meta information:

`midi_extractor.sh create path/to/my/midi/files/ my_database.db`

Then you can use the meta information stored in the database to extract midi files, e.g.:

`midi_extractor.sh extract my_database.db guitars category=guitar`


 
 