# json2code

##About
json2code's main functionality is to:

1. Sample few RESTful API endpoints for some data examples
2. Parse json responses
3. Predict json value types and possible references to other endpoints/data models
4. Verify those predictions by cross-checking each parsed data example
5. Generate Apple's Swift classes with fromJson and toJson methods 

## Parser
Since Compilation Techniques class is focusing on low-level data parsing and compilation tasks, I've decided to ditch
standard python json lib in favour of actually learning something and developing my own parser and scanner. 
Parser accepts unicode json data and returns out python dict which is enriched a bit for my own data-analysis purposes.
Right now the interface is not as user-friendly as I'd like it to be, but it surely will change with later commits.

## JSONValueModel
This little class tries to guess what type of value it holds (which is not at all difficult for python's built-in types)
and if this value is a possible reference to any other object. The first part is relatively easy and is done by either
checking the value type or by checking field's name (e.g. "id" type is predicted by searching for... "id" in the name).
The second part of predicting is also done by checking the field's name, but it will most likely change to something 
more accurate.

## Motivation
json2code is a small project implemented entirely by me in order to pass Compilation Techniques class on Faculty 
of Electronics and Information Technology on Warsaw University of Technology. 
The class focuses on mechanism such as parsers or scanners (lexers) and on other compilation related tasks.

The motivation behind the tool itself is simple: even though there is a lot of support for JSON format in many
programming languages, the support for seamless JSON<->Object transitions is not as commonly found, especially in 
Apple's Swift. I've stumbled upon this little disadvantage in a few projects and tried to find a tool that will
translate JSON to class definitions but I've found none. CT class seamed like a nice opportunity to create such a tool.