import inspect
from collections import OrderedDict, namedtuple

from coalib.misc.Decorators import generate_eq, generate_repr
from coalib.misc.Enum import enum


@generate_repr()
@generate_eq("documentation", "markers", "textrange")
class DocumentationComment:
    """
    The DocumentationComment holds information about a documentation comment
    inside source-code, like position etc.
    """
    _ParseMode = enum("DESCRIPTION", "PARAM", "RETVAL")

    def __init__(self, documentation, markers, textrange):
        """
        Instantiates a new DocumentationComment.

        :param documentation: The documentation text.
        :param markers:       The three-element tuple with marker strings that
                              identified this documentation comment.
        :param textrange:     The position range of type TextRange.
        """
        self.documentation = documentation
        self.markers = markers
        self.textrange = textrange

    # def __str__(self):
    #     return self.documentation.description

    @classmethod
    def from_docstring(cls, docstring):
        """
        Parses a python docstring. Usable attributes are:
        :param
        @param
        :return
        @return
        """
        lines = inspect.cleandoc(docstring).split("\n")

        parse_mode = cls._ParseMode.DESCRIPTION
        cur_param = ""

        desc = ""
        param_dict = OrderedDict()
        retval_desc = ""
        for line in lines:
            line = line.strip()

            if line.startswith(":param ") or line.startswith("@param "):
                parse_mode = cls._ParseMode.PARAM
                splitted = line[7:].split(":", 1)
                cur_param = splitted[0]
                param_dict[cur_param] = splitted[1].strip()

                continue

            if line.startswith(":return: ") or line.startswith("@return: "):
                parse_mode = cls._ParseMode.RETVAL
                retval_desc = line[9:].strip()

                continue

            def concat_doc_parts(old: str, new: str):
                if new != '' and not old.endswith('\n'):
                    return old + ' ' + new

                return old + (new if new != '' else '\n')

            if parse_mode == cls._ParseMode.RETVAL:
                retval_desc = concat_doc_parts(retval_desc, line)
            elif parse_mode == cls._ParseMode.PARAM:
                param_dict[cur_param] = concat_doc_parts(param_dict[cur_param],
                                                         line)
            else:
                desc = concat_doc_parts(desc, line)

        DocComment = namedtuple('DocComment', 'description, params, retval')

        return (DocComment(description=desc.strip(),
                           params=param_dict,
                           retval=retval_desc.strip()))
