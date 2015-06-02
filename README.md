# json2code

## About
json2code's main functionality is to:

1. Parse json data examples
2. Cross-check parsed objects for possible references to other objects
3. Generate canonical data model (metamodel) in a form of editable json files
4. Generate Apple's Swift classes from the metamodel

## The process
### Parser
Since Compilation Techniques class is focusing on low-level data parsing and compilation tasks, I've decided to ditch
standard python json lib in favour of actually learning something and developing my own parser and scanner. 
Parser accepts unicode json data and returns out python dict which is enriched a bit for my own data-analysis purposes.
Right now the interface is not as user-friendly as I'd like it to be, but it surely will change with later commits.

### CDM (Metamodel) generator
Metamodel is generated from parsed data examples and contains information about object structure, namely: 

  * field names
  * field datatypes (int, float, string, bool, date)
  * field relations with other objects

This processing step allows for easier data manipulation in case of data model extensions or other fixes. 
Furthermore it's a basis for extending json2code on other languages which are not 100% json compatible.
Object relations prediction is turned off by default. 

### Swift code generator
This is the final step of the json2code's process. Metamodel is read and its integrity and syntax is verified.
Then Swift code is generated from available json configuration files. 

## Motivation
json2code is a small project implemented in order to pass Compilation Techniques class of Faculty 
of Electronics and Information Technology on Warsaw University of Technology. 
The class focuses on mechanism such as parsers or scanners (lexers) and on other compilation related tasks.

The motivation behind the tool itself is simple: even though there is a lot of support for JSON format in many
programming languages, the support for seamless JSON<->Object transitions is not as commonly found, especially in 
Apple's Swift. I've stumbled upon this little disadvantage in a few projects and tried to find a tool that will
translate JSON to class definitions but I've found none (*well, my searches weren't that far and wide...*).
CT class seamed like a nice opportunity to create such a tool.
