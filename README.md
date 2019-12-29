# What this is
This is a command line tool to process Starbound liquid definition asset files and output the interactions between them.  
Only interactions resulting in liquids are currently output.  

*THE OUTPUT DIRECTORY WILL BE REMOVED, INCLUDING ALL SUBDIRECTORIES AND FILES*
*DO NOT CHOOSE AN OUTPUT DIRECTORY CONTAINING ANYTHING YOU WANT TO KEEP*

# How to use it

`python3 liquids.py <outputdir> <liquiddir1> [liquiddirN ...]`

This will delete (and then recreate) the `outputdir`, and process each `liquiddir`.  
A subdirectory of `outputdir` called `liquids` shall contain every liquid with its comments removed  
and has limited support for patch files (adding liquid interactions in them is supported, but nothing else).  

After running, `outputdir` shall contain 3 JSON files.  
`liquids.json` contains every processed liquid merged into a single dictionary.  
`interactions.json` contains a dict where each key is `"liquidname1 liquidname2"` and the value is the liquid produced.  
`interactions-by-result.json` is a dict where key is the result liquid name,  
and value is a list of `"liquidname1 liquidname2"` entries of the input liquids required.
