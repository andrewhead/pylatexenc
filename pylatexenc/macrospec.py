# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
# 
# Copyright (c) 2019 Philippe Faist
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

r"""
Provides classes and helper functions to describe a LaTeX context of known
macros and environments, specifying how they should be parsed by
:py:mod:`pylatexenc.latexwalker`.

.. versionadded:: 2.0

   The entire module :py:mod:`pylatexenc.macrospec` was introduced in
   `pylatexenc 2.0`.
"""


import sys


if sys.version_info.major > 2:
    # Py3
    def unicode(s): return s
    _basestring = str
    _str_from_unicode = lambda x: x
    _unicode_from_str = lambda x: x
else:
    # Py2
    _basestring = basestring
    _str_from_unicode = lambda x: unicode(x).encode('utf-8')
    _unicode_from_str = lambda x: x.decode('utf-8')


# ------------------------------------------------------------------------------


class ParsedMacroArgs(object):
    r"""
    Parsed representation of macro arguments.

    The base class provides a simple way of storing the arguments as a list of
    parsed nodes.

    This base class can be subclassed to store additional information and
    provide more advanced APIs to access macro arguments for certain categories
    of macros.

    Arguments:

      - `argnlist` is a list of latexwalker nodes that represent macro
        arguments.  If the macro arguments are too complicated to store in a
        list, leave this as `None`.  (But then code that uses the latexwalker
        must be aware of your own API to access the macro arguments.)

        The difference between `argnlist` and the legacy `nodeargs` is that all
        options, regardless of optional or mandatory, are stored in the list
        `argnlist` with possible `None`\ 's at places where optional arguments
        were not provided.  Previously, whether a first optional argument was
        included in `nodeoptarg` or `nodeargs` depended on how the macro
        specification was given.

      - `argspec` is a string or a list that describes how each corresponding
        argument in `argnlist` represents.  If the macro arguments are too
        complicated to store in a list, leave this as `None`.  For standard
        macros and parsed arguments this is a string with characters '*', '[',
        '{' describing an optional star argument, an optional
        square-bracket-delimited argument, and a mandatory argument.

    Attributes:

    .. py:attribute:: argnlist

       The list of latexwalker nodes that was provided to the constructor

    .. py:attribute:: argspec

       Argument type specification provided to the constructor

    .. py:attribute:: legacy_nodeoptarg_nodeargs

       A tuple `(nodeoptarg, nodeargs)` that should be exposed as properties in
       :py:class:`~pylatexenc.latexwalker.LatexMacroNode` to provide (as best as
       possible) compatibility with pylatexenc < 2.

       This is either `(<1st optional arg node>, <list of remaining args>)` if
       the first argument is optional and all remaining args are mandatory; or
       it is `(None, <list of args>)` for any other argument structure.
    """
    def __init__(self, argnlist=[], argspec='', **kwargs):
        super(ParsedMacroArgs, self).__init__(**kwargs)
        
        self.argnlist = argnlist
        self.argspec = argspec

        # for LatexMacroNode to provide some kind of compatibility with pylatexenc < 2
        self.legacy_nodeoptarg_nodeargs = \
            self._get_legacy_attribs(self.argspec, self.argnlist)

    def _get_legacy_attribs(self, argspec, argnlist):
        nskip = 0
        while argspec.startswith('*'):
            argspec = argspec[1:]
            nskip += 1
        if argspec[0:1] == '[' and all(x == '{' for x in argspec[1:]):
            return ( argnlist[nskip], argnlist[nskip+1:] )
        else:
            return (None, argnlist)

        
    def to_json_object(self):
        r"""
        Return a representation of the current parsed arguments in an object that
        our main JSON exporter
        (:py:class:`pylatexenc.latexwalker.LatexNodesJSONEncoder`) can
        understand and export to JSON.

        Called when we export the node structure to JSON (e.g., latexwalker in
        command-line).
        """

        return dict(
            argspec=self.argspec,
            argnlist=self.argnlist,
        )

    def __repr__(self):
        return "{}(argspec={!r}, argnlist={!r})".format(
            self.__class__.__name__, self.argspec, self.argnlist
        )



class MacroStandardArgsParser(object):
    r"""
    Parses the arguments to a LaTeX macro.

    This class parses a simple macro argument specification with a specified
    arrangement of optional and mandatory arguments.

    This class also serves as base class for more advanced argument parsers
    (e.g. for a ``\verb+...+`` macro argument parser).  In such cases,
    subclasses should attempt to provide the most suitable `argspec` (and
    `argnlist` for the corresponding :py:class:`ParsedMacroArgs`) for their use,
    if appropriate, or set them to `None`.

    Arguments:

      - `argspec`: must be a string in which each character corresponds to an
        argument.  The character '{' represents a mandatory argument (single
        token or LaTeX group) and the character '[' denotes an optional argument
        delimited by braces.  The character '\*' denotes a possible star char at
        that position in the argument list, a corresponding
        ``latexwalker.LatexCharsNode('*')`` (or `None` if no star) will be
        inserted in the argument node list.  For instance, the string '\*{[[{'
        would be suitable to specify the signature of the '\\newcommand' macro.

        Currently, the argspec string may only contain the characters '\*', '{'
        and '['.

        The `argspec` may also be `None`, which is the same as specifying an
        empty string.

      - `optional_arg_no_space`: If set to `True`, then an optional argument
        cannot have any whitespace between the preceeding tokens and the '['
        character.  Set this to `True` in cases such as for ``\\`` in AMS-math
        environments, where AMS apparently introduced a patch to prevent a
        bracket on a new line after ``\\`` from being interpreted as the
        optional argument to ``\\``.
    
      - `args_math_mode`: Either `None`, or a list of the same length as
        `argspec`.  If a list is given, then each item must be `True`, `False`,
        or `None`.  The corresponding argument (cf. `argspec`) is then
        respectively parsed in math mode (`True`), in text mode (`False`), or
        with the mode unchanged (`None`).  If `args_math_mode` is `None`, then
        all arguments are parsed in the same mode as the current mode.

      - additional unrecognized keyword arguments are passed on to superclasses
        in case of multiple inheritance

    Attributes:

    .. py:attribute:: argspec

       Argument type specification provided to the constructor.

    .. py:attribute:: optional_arg_no_space

       See the corresponding constructor argument.

    .. py:attribute:: args_math_mode

       See the corresponding constructor argument.
    """
    def __init__(self, argspec=None, optional_arg_no_space=False,
                 args_math_mode=None, **kwargs):
        super(MacroStandardArgsParser, self).__init__(**kwargs)
        self.argspec = argspec if argspec else ''
        self.optional_arg_no_space = optional_arg_no_space
        self.args_math_mode = args_math_mode
        # catch bugs, make sure that argspec is a string with only accepted chars
        if not isinstance(self.argspec, _basestring) or \
           not all(x in '*[{' for x in self.argspec):
            raise TypeError(
                "argspec must be a string containing chars '*', '[', '{{' only: {!r}"
                .format(self.argspec)
            )
        # non-documented attribute that makes us ignore any leading '*'.  We use
        # this to emulate pylatexenc 1.x behavior when using the MacrosDef()
        # function explicitly
        self._like_pylatexenc1x_ignore_leading_star = False

    def parse_args(self, w, pos, parsing_state=None):
        r"""
        Parse the arguments encountered at position `pos` in the
        :py:class:`~pylatexenc.latexwalker.LatexWalker` instance `w`.

        You may override this function to provide custom parsing of complicated
        macro arguments (say, ``\verb+...+``).  The method will be called by
        keyword arguments, so the argument names should not be altered.

        The argument `w` is the :py:class:`pylatexenc.latexwalker.LatexWalker`
        object that is currently parsing LaTeX code.  You can call methods like
        `w.get_goken()`, `w.get_latex_expression()` etc., to parse and read
        arguments.

        The argument `parsing_state` is the current parsing state in the
        :py:class:`~pylatexenc.latexwalker.LatexWalker` (e.g., are we currently
        in math mode?).  See doc for
        :py:class:`~pylatexenc.latexwalker.ParsingState`.

        This function should return a tuple `(argd, pos, len)` where:

        - `argd` is a :py:class:`ParsedMacroArgs` instance, or an instance of a
          subclass of :py:class:`ParsedMacroArgs`.  The base `parse_args()`
          provided here returns a :py:class:`ParsedMacroArgs` instance.

        - `pos` is the position of the first parsed content.  It should be the
          same as the `pos` argument, except if there is whitespace at that
          position in which case the returned `pos` would have to be the
          position where the argument contents start.

        - `len` is the length of the parsed expression.  You will probably want
          to continue parsing stuff at the index `pos+len` in the string.
        """

        from . import latexwalker

        if parsing_state is None:
            parsing_state = w.make_parsing_state()

        argnlist = []

        if self.args_math_mode is not None and \
           len(self.args_math_mode) != len(self.argspec):
            raise ValueError("Invalid args_math_mode={!r} for argspec={!r}!"
                             .format(self.args_math_mode, self.argspec))

        def get_inner_parsing_state(j):
            if self.args_math_mode is None:
                return parsing_state
            amm = self.args_math_mode[j]
            if amm is None or amm == parsing_state.in_math_mode:
                return parsing_state
            if amm == True:
                return parsing_state.sub_context(in_math_mode=True)
            return parsing_state.sub_context(in_math_mode=False)

        p = pos

        if self._like_pylatexenc1x_ignore_leading_star:
            # ignore any leading '*' character
            tok = w.get_token(p)
            if tok.tok == 'char' and tok.arg == '*':
                p = tok.pos + tok.len

        for j, argt in enumerate(self.argspec):
            if argt == '{':
                (node, np, nl) = w.get_latex_expression(
                    p,
                    strict_braces=False,
                    parsing_state=get_inner_parsing_state(j)
                )
                p = np + nl
                argnlist.append(node)

            elif argt == '[':

                if self.optional_arg_no_space and w.s[p].isspace():
                    # don't try to read optional arg, we don't allow space
                    argnlist.append(None)
                    continue

                optarginfotuple = w.get_latex_maybe_optional_arg(
                    p,
                    parsing_state=get_inner_parsing_state(j)
                )
                if optarginfotuple is None:
                    argnlist.append(None)
                    continue
                (node, np, nl) = optarginfotuple
                p = np + nl
                argnlist.append(node)

            elif argt == '*':
                # possible star.
                tok = w.get_token(p)
                if tok.tok == 'char' and tok.arg.startswith('*'):
                    # has star
                    argnlist.append(
                        w.make_node(latexwalker.LatexCharsNode,
                                    parsing_state=get_inner_parsing_state(j),
                                    chars='*', pos=tok.pos, len=1)
                    )
                    p = tok.pos + 1
                else:
                    argnlist.append(None)

            else:
                raise LatexWalkerError(
                    "Unknown macro argument kind for macro: {!r}".format(argt)
                )

        parsed = ParsedMacroArgs(
            argspec=self.argspec,
            argnlist=argnlist,
        )

        return (parsed, pos, p-pos)


    def __repr__(self):
        return '{}(argspec={!r}, optional_arg_no_space={!r}, args_math_mode={!r})'.format(
            self.__class__.__name__, self.argspec, self.optional_arg_no_space,
            self.args_math_mode
        )
    



# ------------------------------------------------------------------------------

class MacroSpec(object):
    r"""
    Stores the specification of a macro.

    This stores the macro name and instructions on how to parse the macro
    arguments.

    .. py:attribute:: macroname

       The name of the macro, without the leading backslash.

    .. py:attribute:: args_parser

       The parser instance that can understand this macro's arguments.  For
       standard LaTeX macros this is usually a
       :py:class:`MacroStandardArgsParser` instance.

       If you specify a string, then for convenience this is interpreted as an
       argspec argument for :py:class:`MacroStandardArgsParser` and such an
       instance is automatically created.
    """
    def __init__(self, macroname, args_parser=MacroStandardArgsParser(), **kwargs):
        super(MacroSpec, self).__init__(**kwargs)
        self.macroname = macroname
        if isinstance(args_parser, _basestring):
            self.args_parser = MacroStandardArgsParser(args_parser)
        else:
            self.args_parser = args_parser

    def parse_args(self, *args, **kwargs):
        r"""
        Shorthand for calling the :py:attr:`args_parser`\ 's `parse_args()` method.
        See :py:class:`MacroStandardArgsParser`.
        """
        return self.args_parser.parse_args(*args, **kwargs)

    def __repr__(self):
        return 'MacroSpec(macroname=%r, args_parser=%r)'%(self.macroname, self.args_parser)



class EnvironmentSpec(object):
    r"""
    Stores the specification of a LaTeX environment.

    This stores the environment name and instructions on how to parse any
    arguments provided after ``\begin{environment}<args>``.

    .. py:attribute:: environmentname

       The name of the environment, i.e., the argument of ``\begin{...}`` and
       ``\end{...}``.

    .. py:attribute:: args_parser

       The parser instance that can understand this environment's arguments.
       For standard LaTeX environment this is usually a
       :py:class:`MacroStandardArgsParser` instance.

       If you specify a string, then for convenience this is interpreted as an
       argspec argument for :py:class:`MacroStandardArgsParser` and such an
       instance is automatically created.

    .. py:attribute:: is_math_mode

       A boolean that indicates whether or not the contents is to be interpreted
       in Math Mode.  This would be True for environments like
       ``\begin{equation}``, ``\begin{align}``, etc., but False for
       ``\begin{figure}``, etc.

    .. note::

       Starred variants of environments (as in ``\begin{equation*}``) must not
       be specified using an argspec as for macros (e.g., `argspec='*'`).
       Rather, we need to define a separate environment spec for the starred
       variant with the star in the name itself (``EnvironmentSpec('equation*',
       None)``) because the star really is part of the environment name.  If you
       happened to use ``EnvironmentSpec('equation', '*')``, then the parser
       would recognize the expression ``\begin{equation}*`` but not
       ``\begin{equation*}``.
    """
    def __init__(self, environmentname, args_parser=MacroStandardArgsParser(),
                 is_math_mode=False, **kwargs):
        super(EnvironmentSpec, self).__init__(**kwargs)
        self.environmentname = environmentname
        if isinstance(args_parser, _basestring):
            self.args_parser = MacroStandardArgsParser(args_parser)
        else:
            self.args_parser = args_parser
        self.is_math_mode = is_math_mode

    def parse_args(self, *args, **kwargs):
        r"""
        Shorthand for calling the :py:attr:`args_parser`\ 's `parse_args()` method.
        See :py:class:`MacroStandardArgsParser`.
        """
        return self.args_parser.parse_args(*args, **kwargs)

    def __repr__(self):
        return 'EnvironmentSpec(environmentname=%r, args_parser=%r, is_math_mode=%r)'%(
            self.environmentname, self.args_parser, self.is_math_mode
        )



class SpecialsSpec(object):
    r"""
    Specification of a LaTeX "special char sequence": an active char, a
    ligature, or some other non-macro char sequence that has a special meaning.

    For instance, '&', '~', and '``' are considered as "specials".

    .. py:attribute:: specials_chars
    
       The string (one or several characters) that has a special meaning. E.g.,
       '&', '~', '``', etc.

    .. py:attribute:: args_parser
    
       A parser (e.g. :py:class:`MacroStandardArgsParser`) that is invoked when
       the specials is encountered.  Can/should be set to `None` if the specials
       should not parse any arguments (e.g. '~').
    """
    def __init__(self, specials_chars,
                 args_parser=None,
                 **kwargs):
        super(SpecialsSpec, self).__init__(**kwargs)
        self.specials_chars = specials_chars
        self.args_parser = args_parser

    def parse_args(self, *args, **kwargs):
        r"""
        Basically a shorthand for calling the :py:attr:`args_parser`\ 's
        `parse_args()` method.  See :py:class:`MacroStandardArgsParser`.
        
        If however the py:attr:`args_parser` attribute is `None`, then this
        method returns `None`.
        """
        if self.args_parser is None:
            return None
        return self.args_parser.parse_args(*args, **kwargs)

    def __repr__(self):
        return 'SpecialsSpec(specials_chars=%r, args_parser=%r)'%(
            self.specials_chars, self.args_parser
        )


# ------------------------------------------------------------------------------


def std_macro(macname, *args, **kwargs):
    r"""
    Return a macro specification for the given macro.  Syntax::
    
      spec = std_macro(macname, argspec)
      #  or
      spec = std_macro(macname, optarg, numargs)
      #  or
      spec = std_macro( (macname, argspec), )
      #  or
      spec = std_macro( (macname, optarg, numargs), )
      #  or
      spec = std_macro( spec ) # spec is already a `MacroSpec` -- no-op

    - `macname` is the name of the macro, without the leading backslash.

    - `argspec` is a string either characters "\*", "{" or "[", in which star
      indicates an optional asterisk character (e.g. starred macro variants),
      each curly brace specifies a mandatory argument and each square bracket
      specifies an optional argument in square brackets.  For example, "{{\*[{"
      expects two mandatory arguments, then an optional star, an optional
      argument in square brackets, and then another mandatory argument.

      `argspec` may also be `None`, which is the same as ``argspec=''``.

    - `optarg` may be one of `True`, `False`, or `None`, corresponding to these
      possibilities:

      + if `True`, the macro expects as first argument an optional argument in
        square brackets. Then, `numargs` specifies the number of additional
        mandatory arguments to the command, given in usual curly braces (or
        simply as one TeX token like a single macro)

      + if `False`, the macro only expects a number of mandatory arguments given
        by `numargs`. The mandatory arguments are given in usual curly braces
        (or simply as one TeX token like a single macro)

      + if `None`, then `numargs` is a string like `argspec` above.  I.e.,
        ``std_macro(macname, None, argspec)`` is the same as
        ``std_macro(macname, argspec)``.

    - `numargs`: depends on `optarg`, see above.
    
    To make environment specifications (:py:class:`EnvironmentSpec`) instead of
    a macro specification, use the function :py:func:`std_environment()`
    instead.

    The helper function :py:func:`std_environment()` is a shorthand for calling
    this function with additional keyword arguments.  An optional keyword
    argument `make_environment_spec=True` to the present function may be
    specified to return an `EnvironmentSpec` instead of a `MacroSpec`.  In this
    case, you can further specify the `environment_is_math_mode=True|False` to
    specify whether of not the environment represents a math mode.
    """

    if isinstance(macname, tuple):
        if len(args) != 0:
            raise TypeError("No positional arguments expected if first argument is a tuple")
        args = tuple(macname[1:])
        macname = macname[0]

    if isinstance(macname, MacroSpec):
        if len(args) != 0:
            raise TypeError("No positional arguments expected if first argument is a MacroSpec")
        return macname
    
    if isinstance(macname, EnvironmentSpec):
        if len(args) != 0:
            raise TypeError("No positional arguments expected if first argument is a EnvironmentSpec")
        return macname

    if len(args) == 1:
        # std_macro(macname, argspec)
        argspec = args[0]
    elif len(args) != 2:
        raise TypeError(
            "Wrong number of arguments for std_macro, macname={!r}, args={!r}".format(
                macname, args
            ))
    elif not args[0] and isinstance(args[1], _basestring):
        # argspec given in numargs
        argspec = args[1]
    else:
        argspec = ''
        if args[0]:
            argspec = '['
        argspec += '{'*args[1]

    if kwargs.get('make_environment_spec', False):
        return EnvironmentSpec(macname, args_parser=MacroStandardArgsParser(argspec),
                               is_math_mode=kwargs.get('environment_is_math_mode', False))
    return MacroSpec(macname, args_parser=MacroStandardArgsParser(argspec))


def std_environment(envname, *args, **kwargs):
    r"""
    Return an environment specification for the given environment.  Syntax::

      spec = std_environment(envname, argspec, is_math_mode=True|False)
      #  or
      spec = std_environment(envname, optarg, numargs, is_math_mode=True|False)
      #  or
      spec = std_environment( (envname, argspec), is_math_mode=True|False)
      #  or
      spec = std_environment( (envname, optarg, numargs), is_math_mode=True|False)
      #  or
      spec = std_environment( spec ) # spec is already a `EnvironmentSpec` -- no-op

    - `envname` is the name of the environment, i.e., the argument to
      ``\begin{...}``.

    - `argspec` is a string either characters "\*", "{" or "[", in which star
      indicates an optional asterisk character (e.g. starred environment
      variants), each curly brace specifies a mandatory argument and each square
      bracket specifies an optional argument in square brackets.  For example,
      "{{\*[{" expects two mandatory arguments, then an optional star, an
      optional argument in square brackets, and then another mandatory argument.

      `argspec` may also be `None`, which is the same as ``argspec=''``.

    .. note::

       See :py:class:`EnvironmentSpec` for an important remark about starred
       variants for environments.  TL;DR: a starred verison of an environment is
       defined as a separate `EnvironmentSpec` with the star in the name and
       *not* using an ``argspec='*'``.

    - `optarg` may be one of `True`, `False`, or `None`, corresponding to these
      possibilities:

      + if `True`, the environment expects as first argument an optional argument in
        square brackets. Then, `numargs` specifies the number of additional
        mandatory arguments to the command, given in usual curly braces (or
        simply as one TeX token like a single environment)

      + if `False`, the environment only expects a number of mandatory arguments given
        by `numargs`. The mandatory arguments are given in usual curly braces
        (or simply as one TeX token like a single environment)

      + if `None`, then `numargs` is a string like `argspec` above.  I.e.,
        ``std_environment(envname, None, argspec)`` is the same as
        ``std_environment(envname, argspec)``.

    - `numargs`: depends on `optarg`, see above.

    - `is_math_mode`: if set to True, then the environment represents a math
      mode environment (e.g., 'equation', 'align', 'gather', etc.), i.e., whose
      contents should be parsed in an appropriate math mode.  Note that
      `is_math_mode` *must* be given as a keyword argument, in contrast to all
      other arguments which must be positional (non-keyword) arguments.
    """
    is_math_mode = kwargs.pop('is_math_mode', False)
    kwargs2 = dict(kwargs)
    kwargs2.update(make_environment_spec=True,
                   environment_is_math_mode=is_math_mode)
    return std_macro(envname, *args, **kwargs2)


def std_specials(specials_chars):
    r"""
    Return a latex specials specification for the given character sequence.  Syntax::

      spec = std_specials(specials_chars)

    where `specials_chars` is the sequence of characters that has a special
    LaTeX meaning, e.g. ``&`` or ``''``.

    This helper function only allows to create specs for simple specials without
    any argument parsing.  For more complicated specials, you can instantiate a
    :py:class:`SpecialsSpec` directly.
    """
    return SpecialsSpec(specials_chars, args_parser=None)




# ------------------------------------------------------------------------------




class LatexContextDb(object):
    r"""
    Store a database of specifications of known macros, environments, and other
    latex specials.  This might be, e.g., how many arguments a macro accepts, or
    how to determine the text representation of a macro or environment.

    When used with :py:class:`pylatexenc.latexwalker.LatexWalker`, the
    specifications describe mostly rules for parsing arguments of macros and
    environments, and which sequences of characters to consider as "latex
    specials".  Specifications for macros, environments, and other specials are
    stored as :py:class:`MacroSpec`, :py:class:`EnvironmentSpec`, and
    :py:class:`SpecialsSpec` instances, respectively.
    When used with :py:class:`pylatexenc.latex2text.LatexNodes2Text`, the
    specifications for macros, environments, and other specials are stored as
    :py:class:`pylatexenc.latex2text.MacroTextSpec` ,
    :py:class:`pylatexenc.latex2text.EnvironmentTextSpec`, and
    :py:class:`pylatexenc.latex2text.SpecialsTextSpec` instances, respectively.

    In fact, the objects stored in this database may be of any type, except that
    macro specifications must have an attribute `macroname`, environment
    specifications must have an attribute `environmentname`, and specials
    specification must have an attribute `specials_chars`.

    The `LatexContextDb` instance is meant to be (pseudo-)immutable.  Once
    constructed and all the definitions added with
    :py:meth:`add_context_category()`, one should refrain from modifying it
    directly after providing it to, e.g., a
    :py:class:`~pylatexenc.latexwalker.LatexWalker` object.  The reason is that
    the latex walker keeps track of what the latex context was when parsing
    nodes, and modifying the context will modify that stored information, too.
    Instead of being tempted to modify the object, create a new one with
    :py:meth:`filter_context()`.

    See :py:func:`pylatexenc.latexwalker.get_default_latex_context_db()` for the
    default latex context for `latexwalker` with a default collection of known
    latex macros and environments.
    See :py:func:`pylatexenc.latex2text.get_default_latex_context_db()` for the
    default latex context for `latex2text` with a set of text replacements for a
    collection of known macros and environments.
    """
    def __init__(self, **kwargs):
        super(LatexContextDb, self).__init__(**kwargs)

        self.category_list = []
        self.d = {}

        self.unknown_macro_spec = None
        self.unknown_environment_spec = None
        self.unknown_specials_spec = None

        
    def add_context_category(self, category, macros=[], environments=[], specials=[],
                             prepend=False, insert_before=None, insert_after=None):
        r"""
        Register a category of macro and environment specifications in the context
        database.

        The category name `category` must not already exist in the database.

        The argument `macros` is an iterable (e.g., a list) of macro
        specification objects.  The argument `environments` is an iterable
        (e.g., a list) of environment spec objects.  Similarly, the `specials`
        argument is an iterable of latex specials spec instances.

        If you specify `prepend=True`, then macro and environment lookups will
        prioritize this category over other categories.  Categories are normally
        searched for in the order they are registered to the database; if you
        specify `prepend=True`, then the new category is prepended to the
        existing list so that it is searched first.

        If `insert_before` is not `None`, then it must be a string; the
        definitions are inserted in the category list immediately before the
        given category name, or at the beginning of the list if the given
        category doesn't exist.  If `insert_after` is not `None`, then it must
        be a string; the definitions are inserted in the category list
        immediately after the given category name, or at the end of the list if
        the given category doesn't exist.

        You may only specify one of `prepend=True`, `insert_before='...'` or
        `insert_after='...'`.
        """
        
        if category in self.category_list:
            raise ValueError("Category {} is already registered in the context database"
                             .format(category))

        # ensure only one of these options is set
        if len([ x for x in (prepend, insert_before, insert_after) if x ]) > 1:
            raise TypeError("add_context_category(): You may only specify one of "
                            "prepend=True, insert_before=... or insert_after=...")

        if prepend:
            self.category_list.insert(0, category)
        elif insert_before:
            if insert_before in self.category_list:
                i = self.category_list.index(insert_before)
            else:
                i = 0
            self.category_list.insert(i, category)
        elif insert_after:
            if insert_after in self.category_list:
                i = self.category_list.index(insert_after) + 1 # insert after found category
            else:
                i = len(self.category_list)
            self.category_list.insert(i, category)
        else:
            self.category_list.append(category)

        self.d[category] = {
            'macros': dict( (m.macroname, m) for m in macros ),
            'environments': dict( (e.environmentname, e) for e in environments ),
            'specials': dict( (s.specials_chars, s) for s in specials ),
        }
        
    def set_unknown_macro_spec(self, macrospec):
        r"""
        Set the macro spec to use when encountering a macro that is not in the
        database.
        """
        self.unknown_macro_spec = macrospec

    def set_unknown_environment_spec(self, environmentspec):
        r"""
        Set the environment spec to use when encountering a LaTeX environment that
        is not in the database.
        """
        self.unknown_environment_spec = environmentspec

    def set_unknown_specials_spec(self, specialsspec):
        r"""
        Set the latex specials spec to use when encountering a LaTeX environment
        that is not in the database.
        """
        self.unknown_specials_spec = specialsspec

    def categories(self):
        r"""
        Return a list of valid category names that are registered in the current
        database context.
        """
        return list(self.category_list)

    def get_macro_spec(self, macroname):
        r"""
        Look up a macro specification by macro name.  The macro name is searched for
        in all categories one by one and the first match is returned.

        Returns a macro spec instance that matches the given `macroname`.  If
        the macro name was not found, we return the default macro specification
        set by :py:meth:`set_unknown_macro_spec()` or `None` if no such spec was
        set.
        """
        for cat in self.category_list:
            # search categories in the given order
            if macroname in self.d[cat]['macros']:
                return self.d[cat]['macros'][macroname]
        return self.unknown_macro_spec
    
    def get_environment_spec(self, environmentname):
        r"""
        Look up an environment specification by environment name.  The environment
        name is searched for in all categories one by one and the first match is
        returned.

        Returns the environment spec.  If the environment name was not found, we
        return the default environment specification set by
        :py:meth:`set_unknown_environment_spec()` or `None` if no such spec was
        set.
        """
        for cat in self.category_list:
            # search categories in the given order
            if environmentname in self.d[cat]['environments']:
                return self.d[cat]['environments'][environmentname]
        return self.unknown_environment_spec

    def get_specials_spec(self, specials_chars):
        r"""
        Look up a "latex specials" specification by character sequence.  The
        sequence name is searched for in all categories one by one and the first
        match is returned.

        If you are parsing a chunk of LaTeX code, you should use
        :py:meth:`test_for_specials()` instead.  Unlike
        :py:meth:`test_for_specials()`, :py:meth:`get_specials_spec()` returns
        the first match regardless of matched length.  [Rationale: we only need
        to worry about matching the longest specials sequence when parsing LaTeX
        code.  Calling `get_specials_spec()` means one has already parsed the
        sequence and one is looking up additional specs on it.]

        Returns the specials spec.  If the latex specials was not found, we
        return the default latex specials specification set by
        :py:meth:`set_unknown_specials_spec()` or `None` if no such spec was
        set.
        """
        for cat in self.category_list:
            # search categories in the given order
            if specials_chars in self.d[cat]['specials']:
                return self.d[cat]['specials'][specials_chars]
        return self.unknown_specials_spec

    def test_for_specials(self, s, pos, parsing_state=None):
        r"""
        Test the given position in the string for any LaTeX specials.  The lookup
        proceeds by searching for in all categories one by one and the first
        match is returned, except that the longest match accross all categories
        is returned.  For instance, a match of '``' in a later category will
        take precedence over a match of '`' in a earlier-searched category.

        Returns a specials spec instance, or `None` if no specials are detected
        at the position `pos`.
        """
        best_match_len = 0
        best_match_s = None
        for cat in self.category_list:
            # search categories in the given order
            for specials_chars in self.d[cat]['specials'].keys():
                if len(specials_chars) > best_match_len and s.startswith(specials_chars, pos):
                    best_match_s = self.d[cat]['specials'][specials_chars]
                    best_match_len = len(specials_chars)

        return best_match_s # this is None if no match

    def iter_macro_specs(self, categories=None):
        r"""
        Yield the macro specs corresponding to all macros in the given categories.

        If `categories` is `None`, then the known macro specs from all
        categories are provided in one long iterable sequence.  Otherwise,
        `categories` should be a list or iterable of category names (e.g.,
        'latex-base') of macro specs to return.

        The macro specs from the different categories specified are concatenated
        into one long sequence which is yielded spec by spec.
        """

        if categories is None:
            categories = self.category_list

        for c in categories:
            if c not in self.category_list:
                raise ValueError("Invalid latex macro spec db category: {!r} (Expected one of {!r})"
                                 .format(c, self.category_list))
            for spec in self.d[c]['macros'].values():
                yield spec

    def iter_environment_specs(self, categories=None):
        r"""
        Yield the environment specs corresponding to all environments in the given
        categories.

        If `categories` is `None`, then the known environment specs from all
        categories are provided in one long iterable sequence.  Otherwise,
        `categories` should be a list or iterable of category names (e.g.,
        'latex-base') of environment specs to return.

        The environment specs from the different categories specified are
        concatenated into one long sequence which is yielded spec by spec.
        """

        if categories is None:
            categories = self.category_list

        for c in categories:
            if c not in self.category_list:
                raise ValueError(
                    "Invalid latex environment spec db category: {!r} (Expected one of {!r})"
                    .format(c, self.category_list)
                )
            for spec in self.d[c]['environments'].values():
                yield spec

    def iter_specials_specs(self, categories=None):
        r"""
        Yield the specials specs corresponding to all environments in the given
        categories.

        If `categories` is `None`, then the known specials specs from all
        categories are provided in one long iterable sequence.  Otherwise,
        `categories` should be a list or iterable of category names (e.g.,
        'latex-base') of specials specs to return.

        The specials specs from the different categories specified are
        concatenated into one long sequence which is yielded spec by spec.
        """

        if categories is None:
            categories = self.category_list

        for c in categories:
            if c not in self.category_list:
                raise ValueError("Invalid latex environment spec db category: {!r} (Expected one of {!r})"
                                 .format(c, self.category_list))
            for spec in self.d[c]['specials'].values():
                yield spec


    def filter_context(self, keep_categories=[], exclude_categories=[],
                       keep_which=[]):
        r"""
        Return a new :py:class:`LatexContextDb` instance where we only keep
        certain categories of macro and environment specifications.
        
        If `keep_categories` is set to a nonempty list, then the returned
        context will not contain any definitions that do not correspond to the
        specified categories.

        If `exclude_categories` is set to a nonempty list, then the returned
        context will not contain any definitions that correspond to the
        specified categories.

        It is explicitly fine to have category names in `keep_categories` and
        `exclude_categories` that don't exist in the present object
        (cf. :py:meth:`categories()`).

        The argument `keep_which`, if non-empty, specifies which definitions to
        keep.  It should be a subset of the list ['macros', 'environments',
        'specials'].
        
        The returned context will make a copy of the dictionaries that store the
        macro and environment specifications, but the specification classes (and
        corresponding argument parsers) might correspond to the same instances.
        I.e., the returned context is not a full deep copy.
        """
        
        new_context = LatexContextDb()

        new_context.unknown_macro_spec = self.unknown_macro_spec
        new_context.unknown_environment_spec = self.unknown_environment_spec
        new_context.unknown_specials_spec = self.unknown_specials_spec

        keep_macros = not keep_which or 'macros' in keep_which
        keep_environments = not keep_which or 'environments' in keep_which
        keep_specials = not keep_which or 'specials' in keep_which

        for cat in self.category_list:
            if keep_categories and cat not in keep_categories:
                continue
            if exclude_categories and cat in exclude_categories:
                continue

            # include this category
            new_context.add_context_category(
                cat,
                macros=self.d[cat]['macros'].values() if keep_macros else [],
                environments=self.d[cat]['environments'].values() if keep_environments else [],
                specials=self.d[cat]['specials'].values() if keep_specials else [],
            )

        return new_context



# ------------------------------------------------------------------------------

from ._macrospec_argparsers import ParsedVerbatimArgs, VerbatimArgsParser
