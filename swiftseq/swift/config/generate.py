class SwiftConfigProp(object):
    NO_QUOTE = '{key}: {val}'

    def __init__(self, key, value, sep=': ', override=None):
        self.key = key
        self.value = value
        self.sep = sep
        self.override = override

    def __str__(self):
        if self.override:
            try:
                return self.override.format(key=self.key, val=self.value)
            except KeyError:
                # If user provides a bad override, go with default
                pass

        return '{key}{sep}{val}'.format(
            key=self.key,
            sep=self.sep,
            val='"{}"'.format(self.value) if isinstance(self.value, str) else self.value
        )

    def __unicode__(self):
        return self.__str__()


class SwiftConfigBlock(object):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.level = kwargs.get('level', 0)
        self.indent_char = kwargs.get('indent_char', '\t')

        self._children = args
        self._children_level = self.level + 1

    def set_level(self, new_level):
        self.level = new_level
        self._children_level = self.level + 1

    def __str__(self):
        block_str = '{indent}{name} {{\n{children}{indent}}}'
        children_str = ''
        for child in self._children:
            if isinstance(child, SwiftConfigProp):
                children_str += '{indent}{child}\n'.format(
                    indent=self.indent_char * self._children_level,
                    child=str(child)
                )
            elif isinstance(child, SwiftConfigBlock):
                child.set_level(self._children_level)
                children_str += '{child}\n'.format(
                    child=str(child)
                )
        return block_str.format(
            indent=self.indent_char * self.level,
            name=self.name,
            children=children_str
        )

    def __unicode__(self):
        return self.__str__()
