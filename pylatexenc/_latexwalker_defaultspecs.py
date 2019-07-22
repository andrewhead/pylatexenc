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


# Internal module. May change without notice.


from .macrospec import std_macro, std_environment, std_specials, \
    MacroSpec, EnvironmentSpec, MacroStandardArgsParser, VerbatimArgsParser

specs = [
    #
    # CATEGORY: latex-base
    #
    ('latex-base', {
        'macros': [

            std_macro('documentclass', True, 1),
            std_macro('usepackage', True, 1),
            std_macro('selectlanguage', True, 1),
            std_macro('setlength', True, 2),
            std_macro('addlength', True, 2),
            std_macro('setcounter', True, 2),
            std_macro('addcounter', True, 2),
            std_macro('newcommand', "*{[[{"),
            std_macro('renewcommand', "*{[[{"),
            std_macro('providecommand', "*{[[{"),
            std_macro('newenvironment', "*{[[{{"),
            std_macro('renewenvironment', "*{[[{{"),
            std_macro('provideenvironment', "*{[[{{"),

            std_macro('DeclareMathOperator', '*{{'),

            std_macro('hspace', False, 1),
            std_macro('vspace', False, 1),

            std_macro('mbox', False, 1),

            # (Note: single backslash) end of line with optional no-break ('*') and
            # additional vertical spacing, e.g. \\*[2mm]
            #
            # Special for this command: don't allow an optional spacing argument
            # to be on a new line.  This emulates the behavior in AMS
            # environments.
            MacroSpec('\\', args_parser=MacroStandardArgsParser('*[', optional_arg_no_space=True)),

            std_macro('item', True, 0),

            # \input{someotherfile}
            std_macro('input', False, 1),
            std_macro('include', False, 1),

            std_macro('includegraphics', True, 1),

            std_macro('chapter', '*[{'),
            std_macro('section', '*[{'),
            std_macro('subsection', '*[{'),
            std_macro('subsubsection', '*[{'),
            std_macro('pagagraph', '*[{'),
            std_macro('subparagraph', '*[{'),


            std_macro('emph', False, 1),
            std_macro('textit', False, 1),
            std_macro('textbf', False, 1),
            std_macro('textsc', False, 1),
            std_macro('textsl', False, 1),
            std_macro('text', False, 1),
            std_macro('mathrm', False, 1),

            std_macro('label', False, 1),
            std_macro('ref', False, 1),
            std_macro('eqref', False, 1),
            std_macro('url', False, 1),
            std_macro('hypersetup', False, 1),
            std_macro('footnote', True, 1),

            std_macro('keywords', False, 1),

            std_macro('hphantom', True, 1),
            std_macro('vphantom', True, 1),

            std_macro("'", False, 1),
            std_macro("`", False, 1),
            std_macro('"', False, 1),
            std_macro("c", False, 1),
            std_macro("^", False, 1),
            std_macro("~", False, 1),
            std_macro("H", False, 1),
            std_macro("k", False, 1),
            std_macro("=", False, 1),
            std_macro("b", False, 1),
            std_macro(".", False, 1),
            std_macro("d", False, 1),
            std_macro("r", False, 1),
            std_macro("u", False, 1),
            std_macro("v", False, 1),

            std_macro("vec", False, 1),
            std_macro("dot", False, 1),
            std_macro("hat", False, 1),
            std_macro("check", False, 1),
            std_macro("breve", False, 1),
            std_macro("acute", False, 1),
            std_macro("grave", False, 1),
            std_macro("tilde", False, 1),
            std_macro("bar", False, 1),
            std_macro("ddot", False, 1),

            std_macro('frac', False, 2),
            std_macro('nicefrac', False, 2),

            std_macro('sqrt', True, 1),

            std_macro('ket', False, 1),
            std_macro('bra', False, 1),
            std_macro('braket', False, 2),
            std_macro('ketbra', False, 2),

            std_macro('texorpdfstring', False, 2),
        ],
        'environments': [
            # NOTE: Starred variants (as in \begin{equation*}) are not specified as
            # for macros with an argspec='*'.  Rather, we need to define a separate
            # spec for the starred variant as the star really is part of the
            # environment name.  If you specify argspec='*', the parser will try to
            # look for an expression of the form '\begin{equation}*'

            std_environment('figure', '['),
            std_environment('figure*', '['),
            std_environment('table', '['),
            std_environment('table*', '['),

            std_environment('abstract', None),
            
            std_environment('tabular', '{'),
            std_environment('tabular*', '{{'),
            std_environment('tabularx', '{[{'),

            std_environment('array', '[{'),

            # AMS environments
            std_environment('equation', None, is_math_mode=True),
            std_environment('equation*', None, is_math_mode=True),
            std_environment('align', None, is_math_mode=True),
            std_environment('align*', None, is_math_mode=True),
            std_environment('gather', None, is_math_mode=True),
            std_environment('gather*', None, is_math_mode=True),
            std_environment('flalign', None, is_math_mode=True),
            std_environment('flalign*', None, is_math_mode=True),
            std_environment('multline', None, is_math_mode=True),
            std_environment('multline*', None, is_math_mode=True),
            std_environment('alignat', '{', is_math_mode=True),
            std_environment('alignat*', '{', is_math_mode=True),
            std_environment('split', None, is_math_mode=True),
        ],
        'specials': [
            std_specials('&'),
            std_specials("~"),
            
            # cf. https://tex.stackexchange.com/a/439652/32188 "fake ligatures":
            std_specials('``'),
            std_specials("''"),
            std_specials("--"),
            std_specials("---"),
            std_specials("!`"),
            std_specials("?`"),

            # TODO --- for this, we need to parse their argument but don't use
            #          the standard args parser because we need to accept,
            #          e.g. "x_\mathrm{initial}"
            #std_specials('^'),
            #std_specials('_'),

        ]}),

    #
    # CATEGORY: verbatim
    #
    ('verbatim', {
        'macros': [
            MacroSpec('verb',
                      args_parser=VerbatimArgsParser(verbatim_arg_type='verb-macro')),
            ],
        'environments': [
            EnvironmentSpec('verbatim',
                            args_parser=VerbatimArgsParser(verbatim_arg_type='verbatim-environment')),
        ],
        'specials': [
            # optionally users could include the specials "|" like in latex-doc
            # for verbatim |\like \this|...
        ]}),

    #
    # CATEGORY: theorems
    #
    ('theorems', {
        'macros': [],
        'environments': [
            std_environment('theorem', '['),
            std_environment('proposition', '['),
            std_environment('lemma', '['),
            std_environment('corollary', '['),
            std_environment('definition', '['),
            std_environment('conjecture', '['),
            std_environment('remark', '['),
            # short names
            std_environment('thm', '['),
            std_environment('prop', '['),
            std_environment('lem', '['),
            std_environment('cor', '['),
            std_environment('conj', '['),
            std_environment('rem', '['),
            std_environment('defn', '['),
        ],
        'specials': [
        ]}),

    #
    # CATEGORY: enumitem
    #
    ('enumitem', {
        'macros': [],
        'environments': [
            std_environment('enumerate', '['),
            std_environment('itemize', '['),
            std_environment('description', '['),
        ],
        'specials': [
        ]}),


    #
    # CATEGORY: latex-ethuebung
    #
    ('latex-ethuebung', {
        'macros': [
            # ethuebung
            std_macro('UebungLoesungFont', False, 1),
            std_macro('UebungHinweisFont', False, 1),
            std_macro('UebungExTitleFont', False, 1),
            std_macro('UebungSubExTitleFont', False, 1),
            std_macro('UebungTipsFont', False, 1),
            std_macro('UebungLabel', False, 1),
            std_macro('UebungSubLabel', False, 1),
            std_macro('UebungLabelEnum', False, 1),
            std_macro('UebungLabelEnumSub', False, 1),
            std_macro('UebungSolLabel', False, 1),
            std_macro('UebungHinweisLabel', False, 1),
            std_macro('UebungHinweiseLabel', False, 1),
            std_macro('UebungSolEquationLabel', False, 1),
            std_macro('UebungTipsLabel', False, 1),
            std_macro('UebungTipsEquationLabel', False, 1),
            std_macro('UebungsblattTitleSeries', False, 1),
            std_macro('UebungsblattTitleSolutions', False, 1),
            std_macro('UebungsblattTitleTips', False, 1),
            std_macro('UebungsblattNumber', False, 1),
            std_macro('UebungsblattTitleFont', False, 1),
            std_macro('UebungTitleCenterVSpacing', False, 1),
            std_macro('UebungAttachedSolutionTitleTop', False, 1),
            std_macro('UebungAttachedSolutionTitleFont', False, 1),
            std_macro('UebungAttachedSolutionTitle', False, 1),
            std_macro('UebungTextAttachedSolution', False, 1),
            std_macro('UebungDueByLabel', False, 1),
            std_macro('UebungDueBy', False, 1),
            std_macro('UebungLecture', False, 1),
            std_macro('UebungProf', False, 1),
            std_macro('UebungLecturer', False, 1),
            std_macro('UebungSemester', False, 1),
            std_macro('UebungLogoFile', False, 1),
            std_macro('UebungLanguage', False, 1),
            std_macro('UebungStyle', False, 1),
            #
            std_macro('uebung', '{['),
            std_macro('exercise', '{['),
            std_macro('keywords', False, 1),
            std_macro('subuebung', False, 1),
            std_macro('subexercise', False, 1),
            std_macro('pdfloesung', True, 1),
            std_macro('pdfsolution', True, 1),
            std_macro('exenumfulllabel', False, 1),
            std_macro('hint', False, 1),
            std_macro('hints', False, 1),
            std_macro('hinweis', False, 1),
            std_macro('hinweise', False, 1),
        ],
        'environments': [
        ],
        'specials': [
        ]
    }),
]
