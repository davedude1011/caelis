from aiogram.types import Message
from aiogram.filters import Filter

import shlex
from typing import Any, List, Literal, Optional, Union

class Command(Filter):
    def __init__(self, keyword: str, prefix = "") -> None:
        self.keyword = keyword
        self.prefix = prefix
    
    async def __call__(self, message: Message) -> bool:
        if not message.text: return False

        return message.text.lower().startswith(self.prefix + self.keyword)


class TagParameterSchema:
    def __init__(self, optional: bool, type: Literal["str", "int", "bool"], description: str) -> None:
        self.optional = optional
        self.type = type
        self.description = description


class TagSchema:
    def __init__(self, key_options: List[str], parameter_list: List[TagParameterSchema]) -> None:
        self.key_options = key_options
        self.parameter_list = parameter_list


class FunctionGroupSchema:
    def __init__(self, title: str, tag_list: List[TagSchema]) -> None:
        self.title = title
        self.tag_list = tag_list

    def generate_help_text(self) -> str:
        lines = [f"Command group: <code>{self.title}</code>\n"]
        for tag in self.tag_list:
            #lines.append(f"{self.title} -{tag.key_options[0]} {" ".join([param.type for param in tag.parameter_list])}")

            aliases = ", ".join([f"<code>-{opt}</code>" if len(opt) < 4 else f"<code>--{opt}</code>" for opt in tag.key_options])
            lines.append(f"{aliases}:")

            if not tag.parameter_list:
                lines.append("    <i>(No parameters)</i>")
                lines.append("")
                continue

            for param in tag.parameter_list:
                optional = "optional" if param.optional else "required"
                lines.append(f"    <i>{param.description}</i>  [{param.type}]  ({optional})")
            
            lines.append("")  # Add an empty line between tags
            

        return "\n".join(lines)


class GlobalTagsSchema:
    def __init__(self, function_groups: Optional[List[FunctionGroupSchema]] = None) -> None:
        self.function_groups = function_groups or []

    def add_function_group(self, function_group: FunctionGroupSchema) -> None:
        self.function_groups.append(function_group)

    def get_group(self, title: str) -> Optional[FunctionGroupSchema]:
        for fg in self.function_groups:
            if fg.title == title:
                return fg
        return None


### === Result classes ===

class ParsedTag:
    def __init__(self, schema: TagSchema, key: str, params: List[Union[str,int,bool]]):
        self.schema = schema
        self.key = key
        self.params = params

    def __repr__(self):
        return f"<ParsedTag key={self.key!r} params={self.params!r}>"


class ParsedCommand:
    def __init__(self, function: FunctionGroupSchema, tags: List[ParsedTag]):
        self.function = function
        self.tags = tags

    def __repr__(self):
        return f"<ParsedCommand func={self.function.title!r} tags={self.tags!r}>"


### === Parser ===

def parse_tags(text: str) -> ParsedCommand:
    # 1) Split into shell-like tokens, respecting quotes
    tokens = shlex.split(text)
    if not tokens:
        raise ValueError("Empty command")

    # 2) Extract and validate the function/group name
    func_name = tokens.pop(0)
    fg = global_tags.get_group(func_name)
    if fg is None:
        raise ValueError(f"Unknown function '{func_name}'")

    parsed: List[ParsedTag] = []
    i = 0
    n = len(tokens)

    while i < n:
        tok = tokens[i]
        if not tok.startswith("-"):
            raise ValueError(f"Expected a tag at position {i+1}, got {tok!r}")

        # strip leading hyphens
        key = tok.lstrip("-")
        i += 1

        # find the matching TagSchema
        schema = next((t for t in fg.tag_list if key in t.key_options), None)
        if schema is None:
            raise ValueError(f"Unknown tag '{tok}' in function '{func_name}'")

        # collect parameters for this tag
        params: List[Union[str,int,bool]] = []
        for param_schema in schema.parameter_list:
            if i < n and not tokens[i].startswith("-"):
                raw = tokens[i]
                # convert to correct type
                if param_schema.type == "int":
                    try:
                        val: Any = int(raw)
                    except ValueError:
                        raise ValueError(f"Expected integer for {key}, got {raw!r}")
                elif param_schema.type == "bool":
                    val = raw.lower() in ("1","true","yes","on")
                else:  # str
                    val = raw
                params.append(val)
                i += 1
            else:
                if param_schema.optional:
                    params.append(None)
                else:
                    raise ValueError(f"Tag '{key}' requires a {param_schema.type} parameter")
        parsed.append(ParsedTag(schema, key, params))

    return ParsedCommand(function=fg, tags=parsed)


global_tags = GlobalTagsSchema()