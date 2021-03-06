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
Parser accepts unicode json data and returns a python dict. Parser can also return a dict which is a bit enriched
for data-analysis purposes. This behavoiour is off by default and can be turned on by setting `simple-value` kwarg
to `False`. 

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

## Canonical Data Model
CDM config is in a form of a json file. It consists of key-value pairs, where the key is interpreted as class 
member's name, and the value as class member's type. Valid basic types are: `string`, `int`, `bool`, `float`, 
`date`, `object` and `array`. Arrays can be specified by adding square brackets around the type specification:
`[int]`.

`object` type is later interpreted as dictionary of `[String: AnyObject]` and `array` type is interpreted as an 
array of `[JSON]`. Both `object` and `array` specify, that the value of a certain field consists of sub-json 
file(s). These types are generated when reference prediction is off. Otherwise, sub-json files are recognized 
as other objects, and their type specification is generated as a reference type. 

Reference types have special formatting, which looks like this: 

`:predicted_type:other_type:another_type:...:full|id|uri`

`:` indicates that the value of a field is a reference to other class, list of `predicted_type:...:` is a list 
of possible type references and `full|id|uri` is an indication of reference method - either a full object dictionary,
id or resource uri.

The `!@#$ORIGIN$#@!` value indicates the file that contained the object which was the base for this configuration 
file. It is optional and generated by the CDM Generator.

Here's an example:

```json
{
	"!@#$ORIGIN$#@!": "user.json",
	"first_name": "string",
	"last_name": "string",
	"post_uris": "[:post:uri]",
	"post_stubs": "[:post:post_stubs:full]",
	"profile_photo": ":photo:profile_photo:full",
	"id": "int"
}
```

Examples of valid CDM configuration paired with json examples can be found in json_examples/config/ and 
json_examples/ respectively.  

## Motivation
json2code is a small project implemented in order to pass Compilation Techniques class of Faculty 
of Electronics and Information Technology on Warsaw University of Technology. 
The class focuses on mechanism such as parsers or scanners (lexers) and on other compilation related tasks.

The motivation behind the tool itself is simple: even though there is a lot of support for JSON format in many
programming languages, the support for seamless JSON<->Object transitions is not as commonly found, especially in 
Apple's Swift. I've stumbled upon this little disadvantage in a few projects and tried to find a tool that will
translate JSON to class definitions but I've found none (*well, my searches weren't that far and wide...*).
CT class seemed like a nice opportunity to create such a tool.
