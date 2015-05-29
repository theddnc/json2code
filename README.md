# json2code

## About
json2code is a small project implemented entirely by me in order to pass Compilation Techniques class on Faculty 
of Electronics and Iformation Technology on Warsaw University of Technology. 
The class focuses on mechanism such as parsers or scanners (lexers) and on other compilation related tasks. json2code's
main functionality is to:

1. Sample few RESTful API endpoints for some data examples
2. Parse json responses
3. Predict json value types and possible references to other endpoints/data models
4. Verify those predictions by cross-checking each parsed data example
5. Generate Apple's Swift classes with fromJson and toJson methods 

## Parser
Since Compilation Techniques class is focusing on low-level data parsing and compilation tasks, I've decided to ditch
standard python json lib in favour of actually learning something and developing my own parser and scanner. 
Parser swallows unicode json data and spits out python dict which is enriched a bit for my own data-analysis purposes.
Right now the interface is not as user-friendly as I'd like it to be, but it surely will change with later commits.

## JSONValueModel
This little class tries to guess what type of value it holds (which is not at all difficult for python's built-in types)
and if this value is a possible reference to any other object. The first part is relatively easy and is done by either
checking the value type or by checking field's name (e.g. "id" type is predicted by searching for... "id" in the name).
The second part of predicting is done by checking everything in the field's name that was not used to predict the 'id' 
or the 'uri' type.