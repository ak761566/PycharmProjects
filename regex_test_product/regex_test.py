import re

input_string = "/pcontent/ongoing/journal_content/INGEST_MASTER/_eReferences/OUP/Fetched/E-References/NEW/ORO/ORO-April-2017/ORO-OxEncyclML-April17Update.zip"
regex_string = "([\\/]pcontent[\\/]ongoing[\\/]journal_content[\\/]INGEST_MASTER[\\/]_eReferences[\\/]OUP[\\/]Fetched[\\/]E-References[\\/]NEW[\\/]ORO[\\/](ORO-.*)[\\/](.*)\.zip)"

prog = re.compile(regex_string)
result  = prog.match(input_string)
#print(result.groupdict())
#print(type(result.groups()))
#print(result.string)
#print(result.end())
#print(result.expand())
print(result.re)