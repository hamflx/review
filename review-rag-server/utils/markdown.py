from typing import Any, Callable, List, Optional

from llama_index.core.node_parser.relational.base_element import Element
from llama_index.core.node_parser.relational.utils import md_to_df
from pydantic import BaseModel


def extract_elements(
    text: str,
    node_id: Optional[str] = None,
    table_filters: Optional[List[Callable]] = None,
    **kwargs: Any,
) -> List[Element]:
    # get node id for each node so that we can avoid using the same id for different nodes
    """Extract elements from text."""
    lines = text.split("\n")
    currentElement = None

    elements: List[Element] = []
    # Then parse the lines
    for line in lines:
        if line.startswith("```"):
            # check if this is the end of a code block
            if currentElement is not None and currentElement.type == "code":
                elements.append(currentElement)
                currentElement = None
                # if there is some text after the ``` create a text element with it
                if len(line) > 3:
                    elements.append(
                        Element(
                            id=f"id_{len(elements)}",
                            type="text",
                            element=line.lstrip("```"),
                        )
                    )

            elif line.count("```") == 2 and line[-3] != "`":
                # check if inline code block (aka have a second ``` in line but not at the end)
                if currentElement is not None:
                    elements.append(currentElement)
                currentElement = Element(
                    id=f"id_{len(elements)}",
                    type="code",
                    element=line.lstrip("```"),
                )
            elif currentElement is not None and currentElement.type == "text":
                currentElement.element += "\n" + line
            else:
                if currentElement is not None:
                    elements.append(currentElement)
                currentElement = Element(
                    id=f"id_{len(elements)}", type="text", element=line
                )

        elif currentElement is not None and currentElement.type == "code":
            currentElement.element += "\n" + line

        elif line.startswith("|"):
            if currentElement is not None and currentElement.type != "table":
                if currentElement is not None:
                    elements.append(currentElement)
                currentElement = Element(
                    id=f"id_{len(elements)}", type="table", element=line
                )
            elif currentElement is not None:
                currentElement.element += "\n" + line
            else:
                currentElement = Element(
                    id=f"id_{len(elements)}", type="table", element=line
                )
        elif line.startswith("#"):
            if currentElement is not None:
                elements.append(currentElement)
            currentElement = Element(
                id=f"id_{len(elements)}",
                type="title",
                element=line.lstrip("#"),
                title_level=len(line) - len(line.lstrip("#")),
            )
        else:
            if currentElement is not None and currentElement.type != "text":
                elements.append(currentElement)
                currentElement = Element(
                    id=f"id_{len(elements)}", type="text", element=line
                )
            elif currentElement is not None:
                currentElement.element += "\n" + line
            else:
                currentElement = Element(
                    id=f"id_{len(elements)}", type="text", element=line
                )
    if currentElement is not None:
        elements.append(currentElement)

    for idx, element in enumerate(elements):
        if element.type == "table":
            should_keep = True
            perfect_table = True

            # verify that the table (markdown) have the same number of columns on each rows
            table_lines = element.element.split("\n")
            table_columns = [len(line.split("|")) for line in table_lines]
            if len(set(table_columns)) > 1:
                # if the table have different number of columns on each rows, it's not a perfect table
                # we will store the raw text for such tables instead of converting them to a dataframe
                perfect_table = False

            # verify that the table (markdown) have at least 2 rows
            if len(table_lines) < 2:
                should_keep = False

            # apply the table filter, now only filter empty tables
            if should_keep and perfect_table and table_filters is not None:
                should_keep = all(tf(element) for tf in table_filters)

            # if the element is a table, convert it to a dataframe
            if should_keep:
                if perfect_table:
                    table = md_to_df(element.element)

                    elements[idx] = Element(
                        id=f"id_{node_id}_{idx}" if node_id else f"id_{idx}",
                        type="table",
                        element=element.element,
                        table=table,
                    )
                else:
                    # for non-perfect tables, we will store the raw text
                    # and give it a different type to differentiate it from perfect tables
                    elements[idx] = Element(
                        id=f"id_{node_id}_{idx}" if node_id else f"id_{idx}",
                        type="table_text",
                        element=element.element,
                        # table=table
                    )
            else:
                elements[idx] = Element(
                    id=f"id_{node_id}_{idx}" if node_id else f"id_{idx}",
                    type="text",
                    element=element.element,
                )

    # merge consecutive text elements together for now
    merged_elements: List[Element] = []
    for element in elements:
        if (
            len(merged_elements) > 0
            and element.type == "text"
            and merged_elements[-1].type == "text"
        ):
            merged_elements[-1].element += "\n" + element.element
        else:
            merged_elements.append(element)
    elements = merged_elements
    return merged_elements


class Group(BaseModel):
    type: str
    title: Optional[str]
    level: Optional[int]
    elements: List[Element]
    pass


def group_elements_by_title(elements: List[Element]) -> List[Group]:
    """
    将 markdown 区块根据标题进行分组。分组依据为第一次出现的标题的类型。
    """
    groups = []

    current_group = None

    first_title_level = None

    for el in elements:
        if el.type == 'title':
            if first_title_level is None and el.title_level is not None:
                first_title_level = el.title_level
            if current_group is None:
                current_group = Group(
                    type=el.type,
                    title=el.element if isinstance(el.element, str) else None,
                    level=el.title_level,
                    elements=[el]
                )
            else:
                if el.title_level and current_group.level and el.title_level > current_group.level:
                    current_group.elements.append(el)
                else:
                    groups.append(current_group)
                    current_group = Group(
                        type=el.type,
                        title=el.element if isinstance(el.element, str) else None,
                        level=el.title_level,
                        elements=[el]
                    )
        else:
            if current_group is None:
                current_group = Group(
                    type='title',
                    title=None,
                    level=None,
                    elements=[el]
                )
            else:
                current_group.elements.append(el)

    if current_group:
        groups.append(current_group)

    return groups
