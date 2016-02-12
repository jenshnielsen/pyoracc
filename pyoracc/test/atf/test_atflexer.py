# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
from itertools import repeat
from unittest import TestCase
from nose.tools import assert_equal  # @UnresolvedImport
from ...atf.atflex import AtfLexer
# Jython does not use a named touple here so we have to just take the first
# element and not major as normal.
if sys.version_info[0] == 2:
    from itertools import izip_longest as zip_longest
else:
    from itertools import zip_longest

lexer = AtfLexer().lexer


class testLexer(TestCase):
    def setUp(self):
        lexerstate = True
        while lexerstate:
            try:
                lexer.pop_state()
            except IndexError:
                lexerstate = False

    def compare_tokens(self, content, expected_types, expected_values=None):
        lexer.input(content)
        if expected_values is None:
            expected_values = repeat(None)
        for expected_type, expected_value, token in zip_longest(
                expected_types, expected_values, lexer):
            print(token, expected_type)
            if token is None and expected_type is None:
                break
            assert_equal(token.type, expected_type)
            if expected_value:
                # print token.value, expected_value
                assert_equal(token.value, expected_value)

    def test_code(self):
        self.compare_tokens(
            "&X001001 = JCS 48, 089\n",
            ["AMPERSAND", "ID", "EQUALS", "ID", "NEWLINE"],
            [None, "X001001", None, "JCS 48, 089"]
        )

    def test_crlf(self):
        self.compare_tokens(
            "&X001001 = JCS 48, 089\r\n" +
            "#project: cams/gkab\n\r",
            ["AMPERSAND", "ID", "EQUALS", "ID", "NEWLINE"] +
            ["PROJECT", "ID", "NEWLINE"]
        )

    def test_project(self):
        self.compare_tokens(
            "#project: cams/gkab\n",
            ["PROJECT", "ID", "NEWLINE"],
            [None, "cams/gkab", None]
        )

    def test_key(self):
        self.compare_tokens(
            "#key: cdli=ND 02688\n",
            ["KEY", "ID", "EQUALS", "ID", "NEWLINE"],
            [None, "cdli", None, "ND 02688", None]
        )

    def test_language_protocol(self):
        self.compare_tokens(
            "#atf: lang akk-x-stdbab\n",
            ["ATF", "LANG", "ID", "NEWLINE"],
            [None, None, "akk-x-stdbab"]
        )

    def test_use_unicode(self):
        self.compare_tokens(
            "#atf: use unicode\n",
            ["ATF", "USE", "UNICODE", "NEWLINE"]
        )

    def test_use_math(self):
        self.compare_tokens(
            "#atf: use math\n",
            ["ATF", "USE", "MATH", "NEWLINE"]
        )

    def test_use_legacy(self):
        self.compare_tokens(
            "#atf: use legacy\n",
            ["ATF", "USE", "LEGACY", "NEWLINE"]
        )

    def test_bib(self):
        self.compare_tokens(
            "#bib:  MEE 15 54\n",
            ["BIB", "ID", "NEWLINE"]
        )

    def test_link(self):
        self.compare_tokens(
            "#link: def A = P363716 = TCL 06, 44\n" +
            "@tablet\n",
            ["LINK", "DEF", "ID", "EQUALS", "ID", "EQUALS", "ID", "NEWLINE",
             "TABLET", "NEWLINE"],
            [None, None, "A", None, "P363716", None, "TCL 06, 44"]
        )

    def test_link_parallel_slash(self):
        self.compare_tokens(
            "#link: parallel dcclt/obale:P274929 = IM 070209\n" +
            "@tablet\n",
            ["LINK", "PARALLEL", "ID", "EQUALS", "ID", "NEWLINE",
             "TABLET", "NEWLINE"],
            [None, None, "dcclt/obale:P274929", None, "IM 070209"]
        )

    def test_link_parallel(self):
        self.compare_tokens(
            "#link: parallel abcd:P363716 = TCL 06, 44\n" +
            "@tablet\n",
            ["LINK", "PARALLEL", "ID", "EQUALS", "ID", "NEWLINE",
             "TABLET", "NEWLINE"],
            [None, None, "abcd:P363716", None, "TCL 06, 44"]
        )

    def test_link_reference(self):
        self.compare_tokens(
            "|| A o ii 10\n",
            ["PARBAR", "ID", "ID", "ID", "ID", "NEWLINE"]
        )

    def test_link_reference_range(self):
        self.compare_tokens(
            "|| A o ii 10 -  o ii 12 \n",
            ["PARBAR", "ID", "ID", "ID", "ID", "MINUS",
             "ID", "ID", "ID", "NEWLINE"]
        )

    def test_link_reference_prime_range(self):
        self.compare_tokens(
            "|| A o ii 10' -  o ii' 12 \n",
            ["PARBAR", "ID", "ID", "ID", "ID", "MINUS",
             "ID", "ID", "ID", "NEWLINE"]
        )

    def test_score(self):
        self.compare_tokens(
            "@score matrix parsed word\n",
            ["SCORE", "ID", "ID", "ID", "NEWLINE"]
        )

    def test_division_tablet(self):
        self.compare_tokens(
            "@tablet",
            ["TABLET"]
        )

    def test_text_linenumber(self):
        self.compare_tokens(
            "1.    [MU] 1.03-KAM {iti}AB GE₆ U₄ 2-KAM",
            ["LINELABEL"] + ['ID'] * 6
        )

    def test_lemmatize(self):
        self.compare_tokens(
            "#lem: šatti[year]N; n; Ṭebetu[1]MN; " +
            "mūša[at night]AV; ūm[day]N; n",
            ["LEM"] + ['ID', 'SEMICOLON'] * 5 + ['ID']
        )

    def test_loose_dollar(self):
        self.compare_tokens(
            "$ (a loose dollar line)",
            ["DOLLAR", "PARENTHETICALID"],
            [None, "(a loose dollar line)"]
        )

    def test_loose_nested_dollar(self):
        self.compare_tokens(
            "$ (a (very) loose dollar line)",
            ["DOLLAR", "PARENTHETICALID"],
            [None, "(a (very) loose dollar line)"]
        )

    def test_loose_end_nested_dollar(self):
        self.compare_tokens(
            "$ (a loose dollar line (wow))",
            ["DOLLAR", "PARENTHETICALID"],
            [None, "(a loose dollar line (wow))"]
        )

    def test_strict_dollar(self):
        self.compare_tokens(
            "$ reverse blank",
            ["DOLLAR", "REFERENCE", "BLANK"]
        )

    def test_translation_intro(self):
        self.compare_tokens(
            "@translation parallel en project",
            ["TRANSLATION", "PARALLEL", "ID", "PROJECT"]
        )

    def test_translation_text(self):
        self.compare_tokens(
            "@translation parallel en project\n" +
            "1.    Year 63, Ṭebetu (Month X), night of day 2:^1^",
            ["TRANSLATION", "PARALLEL", "ID", "PROJECT", "NEWLINE",
             "LINELABEL", "ID", "HAT", "ID", "HAT"],
            [None, "parallel", "en", "project", None,
             "1", "Year 63, Ṭebetu (Month X), night of day 2:",
             None, '1', None]
        )

    def test_translation_multiline_text(self):
        self.compare_tokens(
            "@translation parallel en project\n" +
            "1.    Year 63, Ṭebetu (Month X)\n" +
            " , night of day 2\n",
            ["TRANSLATION", "PARALLEL", "ID", "PROJECT", "NEWLINE",
             "LINELABEL", "ID", "NEWLINE"],
            [None, "parallel", "en", "project", None,
             "1", "Year 63, Ṭebetu (Month X) , night of day 2", None]
        )

    def test_translation_labeled_text(self):
        self.compare_tokens(
            "@translation labeled en project\n" +
            "@label o 4\n" +
            "Then it will be taken for the rites and rituals.\n\n",
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE",
             "LABEL", "ID", "ID", "NEWLINE",
             "ID", "NEWLINE"],
            [None, "labeled", "en", "project", None,
             None, "o", "4", None,
             'Then it will be taken for the rites and rituals.', None]
        )

    def test_translation_labeled_noted_text(self):
        self.compare_tokens(
            "@translation labeled en project\n" +
            "@label r 8\n" +
            "The priest says the gods have performed these actions. ^1^\n\n" +
            "@note ^1^ Parenthesised text follows Neo-Assyrian source\n",
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE",
             "LABEL", "ID", "ID", "NEWLINE",
             "ID", "HAT", "ID", "HAT", "NEWLINE",
             "NOTE", "HAT", "ID", "HAT", "ID", 'NEWLINE'],
            [None, "labeled", "en", "project", None,
             None, "r", "8", None,
             'The priest says the gods have performed these actions.',
             None, "1", None, None,
             None, None, "1", None,
             "Parenthesised text follows Neo-Assyrian source"]

        )

    def test_translation_labeled_dashlabel(self):
        self.compare_tokens(
            "@translation labeled en project\n" +
            "@label o 14-15 - o 20\n" +
            "You strew all (kinds of) seed.\n\n",
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE",
             "LABEL", "ID", "ID", "MINUS", "ID", "ID", "NEWLINE",
             "ID", "NEWLINE"],
            [None, "labeled", "en", "project", None,
             None, "o", "14-15", None, "o", "20", None]
        )

    def test_translation_labeled_atlabel(self):
        self.compare_tokens(
            "@translation labeled en project\n" +
            "@(o 20) You strew all (kinds of) seed.\n" +
            "@(o i 2) No-one will occupy the king of Akkad's throne.\n\n",
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE",
             "OPENR", "ID", "ID", "CLOSER", "ID", "NEWLINE",
             "OPENR", "ID", "ID", "ID", "CLOSER", "ID", "NEWLINE", ],
            [None, "labeled", "en", "project", None,
             None, "o", "20", None, "You strew all (kinds of) seed.", None,
             None, "o", "i", "2", None,
             "No-one will occupy the king of Akkad's throne.", None, ]
        )

    def test_translation_range_label_prime(self):
        self.compare_tokens(
            "@translation labeled en project\n" +
            "@label r 1' - r 2'\n",
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE",
             "LABEL", "ID", "ID", "MINUS", "ID", "ID", "NEWLINE"],
            [None, "labeled", "en", "project", None,
             None, "r", "1'", None, "r", "2'", None]
        )

    def test_translation_label_unicode_suffix(self):
        self.compare_tokens(
            "@translation labeled en project\n" +
            u'@label r A\u2081\n',
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE",
             "LABEL", "ID", "ID", "NEWLINE"],
            [None, "labeled", "en", "project", None,
             None, "r", u"A\u2081"]
        )

    def test_translation_label_unicode_prime(self):
        self.compare_tokens(
            "@translation labeled en project\n" +
            u'@label r 1\u2019\n',
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE",
             "LABEL", "ID", "ID", "NEWLINE"],
            [None, "labeled", "en", "project", None,
             None, "r", "1'", None]
        )

    def test_translation_label_unicode_prime2(self):
        self.compare_tokens(
            "@translation labeled en project\n" +
            u'@label r 1\xb4\n',
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE",
             "LABEL", "ID", "ID", "NEWLINE"],
            [None, "labeled", "en", "project", None,
             None, "r", "1'", None, "r", "2'", None]
        )

    def test_translation_range_label_plus(self):
        self.compare_tokens(
            "@translation labeled en project\n" +
            "@label+ o 28\n",
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE",
             "LABEL", "ID", "ID", "NEWLINE"]
        )

    def test_translation_label_long_reference(self):
        "Translations can have full surface names rather than single letter"
        self.compare_tokens(
            "@translation labeled en project\n" +
            "@label obverse 28\n",
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE",
             "LABEL", "REFERENCE", "ID", "NEWLINE"]
        )

    def test_translation_symbols_in_translation(self):
        self.compare_tokens(
            "@translation labeled en project\n" +
            "@label o 1'\n" +
            "[...] ... (zodiacal sign) 8, 10° = (sign) 12, 10°\n\n",
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE",
             "LABEL", "ID", "ID", "NEWLINE",
             "ID", "NEWLINE"]
        )

    def test_translation_ats_in_translation(self):
        self.compare_tokens(
            "@translation labeled en project\n" +
            "@label o 1'\n" +
            "@kupputu (means): affliction (@? and) reduction?@;" +
            " they are ... like cisterns.\n\n",
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE",
             "LABEL", "ID", "ID", "NEWLINE",
             "ID", "NEWLINE"]
        )

    def test_translation_blank_line_begins_translation(self):
        # A double newline normally ends a translation paragraph
        # But this is NOT the case at the beginning of a section,
        # Apparently.
        self.compare_tokens(
            "@translation labeled en project\n" +
            "@label o 16\n" +
            "\n" +
            "@šipir @ṭuhdu @DU means: a message of abundance" +
            " will come triumphantly.\n",
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE",
             "LABEL", "ID", "ID", "NEWLINE",
             "ID", "NEWLINE"]
        )

    def test_translation_blank_line_amid_translation(self):
        # A double newline normally ends a translation paragraph
        # But this is NOT the case at the beginning of a section,
        # Apparently.
        self.compare_tokens(
            "@translation labeled en project\n" +
            "@(4) their [cri]mes [have been forgiven] by the king." +
            " (As to) all [the\n" +
            "\n" +
            "    libe]ls that [have been uttered against me " +
            "in the palace, which] he has\n" +
            "\n" +
            "    heard, [I am not guilty of] any [of them! " +
            "N]ow, should there be a\n",
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE",
             "OPENR", "ID", "CLOSER", "ID", "NEWLINE",
             "ID", "NEWLINE", "ID", "NEWLINE"]
        )

    def test_translation_no_blank_line_in_labeled_translation(self):
        # This functionality is expressly forbidden at
        # http://build.oracc.org/doc2/help/editinginatf/translations/index.html
        # But appears is in cm_31_139 anyway
        self.compare_tokens(
            "@translation labeled en project\n" +
            "@label o 13\n" +
            "@al-@ŋa₂-@ŋa₂ @al-@ŋa₂-@ŋa₂ @šag₄-@ba-@ni" +
            " @nu-@sed-@da (means) he will" +
            "remove (... and) he will place (...); his heart will not rest" +
            "It is said in the textual corpus of the lamentation-priests.\n" +
            "@label o 15\n" +
            "Text\n\n",
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE",
             "LABEL", "ID", "ID", "NEWLINE",
             "ID", "NEWLINE",
             "LABEL", "ID", "ID", "NEWLINE",
             "ID", "NEWLINE"]
        )

    def test_translation_range_label_periods(self):
        self.compare_tokens(
            "@translation labeled en project\n" +
            "@label t.e. 1\n",
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE",
             "LABEL", "ID", "ID", "NEWLINE"],
            [None, "labeled", "en", "project", None,
             None, "t.e.", "1"])

    def test_interlinear_translation(self):
        self.compare_tokens(
            "@tablet\n" +
            "1'. ⸢x⸣\n" +
            "#tr: English\n",
            ["TABLET", "NEWLINE",
             "LINELABEL", "ID", "NEWLINE",
             "TR", "ID", "NEWLINE"])

    def test_multilineinterlinear_translation(self):
        self.compare_tokens(
            "@tablet\n" +
            "1'. ⸢x⸣\n" +
            "#tr: English\n" +
            " on multiple lines\n",
            ["TABLET", "NEWLINE",
             "LINELABEL", "ID", "NEWLINE",
             "TR", "ID", "NEWLINE"])

    def test_note_internalflag(self):
        self.compare_tokens(
            "@note Hello James's World",
            ["NOTE", "ID"],
            [None, "Hello James's World"]
        )

    def test_note_internalspace(self):
        self.compare_tokens(
            "@note Hello James",
            ["NOTE", "ID"],
            [None, "Hello James"]
        )

    def test_note_onechar(self):
        self.compare_tokens(
            "@note H",
            ["NOTE", "ID"],
            [None, "H"]
        )

    def test_note_short(self):
        self.compare_tokens(
            "@note I'm",
            ["NOTE", "ID"],
            [None, "I'm"]
        )

    def test_division_note(self):
        self.compare_tokens(
            "@note ^1^ A note to the translation.\n",
            ["NOTE", "HAT", "ID", "HAT", "ID", "NEWLINE"],
            [None, None, "1", None, "A note to the translation.", None]
        )

    def test_hash_note(self):
        self.compare_tokens(
            "@tablet\n" +
            "@obverse\n" +
            "3.    U₄!-BI? 20* [(ina)] 9.30 ina(DIŠ) MAŠ₂!(BAR)\n" +
            "#note: Note to line.\n",
            ["TABLET", "NEWLINE", "OBVERSE", "NEWLINE",
             "LINELABEL"] + ["ID"] * 6 + ["NEWLINE", "NOTE", "ID", "NEWLINE"]
        )

    def test_open_text_with_dots(self):
        # This must not come out as a linelabel of Hello.
        self.compare_tokens(
            "@translation labeled en project\n" +
            "@label o 1\nHello. World\n\n",
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE",
             "LABEL", "ID", "ID", "NEWLINE",
             "ID", "NEWLINE"]
        )

    def test_flagged_object(self):
        self.compare_tokens("@object which is remarkable and broken!#\n",
                            ["OBJECT", "ID", "EXCLAIM", "HASH", "NEWLINE"])

    def test_comment(self):
        self.compare_tokens(
            "# I've added various things for test purposes\n",
            ['COMMENT', "ID", "NEWLINE"]
        )

    def test_nospace_comment(self):
        self.compare_tokens(
            "#I've added various things for test purposes\n",
            ['COMMENT', "ID", "NEWLINE"]
        )

    def test_check_comment(self):
        self.compare_tokens(
            "#CHECK: I've added various things for test purposes\n",
            ['CHECK', "ID", "NEWLINE"]
        )

    def test_dotline(self):
        self.compare_tokens(
            ". \n",
            ['NEWLINE']
        )

    def test_translation_heading(self):
        self.compare_tokens(
            "@translation parallel en project\n" +
            "@h1 A translation heading\n",
            ["TRANSLATION", "PARALLEL", "ID", "PROJECT", "NEWLINE"] +
            ["HEADING", "ID", "NEWLINE"]
        )

    def test_heading(self):
        self.compare_tokens(
            "@obverse\n" +
            "@h1 A heading\n",
            ["OBVERSE", "NEWLINE"] +
            ["HEADING", "ID", "NEWLINE"]
        )

    def test_double_comment(self):
        """Not sure if this is correct; but can't find
        anything in structure or lemmatization doc"""
        self.compare_tokens(
            "## papān libbi[belly] (already in gloss, same spelling)\n",
            ['COMMENT', 'ID', 'NEWLINE']
        )

    def test_ruling(self):
        self.compare_tokens(
            "$ single ruling",
            ["DOLLAR", "SINGLE", "RULING"]
        )

    def test_described_object(self):
        self.compare_tokens(
            "@object An object that fits no other category\n",
            ["OBJECT", "ID", "NEWLINE"],
            [None, "An object that fits no other category"]
        )

    def test_nested_object(self):
        self.compare_tokens(
            "@tablet\n" +
            "@obverse\n",
            ["TABLET", "NEWLINE", "OBVERSE", "NEWLINE"]
        )

    def test_object_line(self):
        self.compare_tokens(
            "@tablet\n" +
            "@obverse\n" +
            "1.    [MU] 1.03-KAM {iti}AB GE₆ U₄ 2-KAM\n"
            "#lem: šatti[year]N; n; Ṭebetu[1]MN; mūša[at night]AV; " +
            "ūm[day]N; n\n",
            ['TABLET', 'NEWLINE',
             "OBVERSE", 'NEWLINE',
             'LINELABEL'] + ['ID'] * 6 + ['NEWLINE', 'LEM'] +
            ['ID', 'SEMICOLON'] * 5 + ['ID', "NEWLINE"]
        )

    def test_dot_in_linelabel(self):
        self.compare_tokens(
            "1.1.    [MU]\n",
            ['LINELABEL', 'ID', 'NEWLINE']
        )

    def test_score_lines(self):
        self.compare_tokens(
            "1.4′. %n ḫašḫūr [api] lal[laga imḫur-līm?]\n" +
            "#lem: ḫašḫūr[apple (tree)]N; api[reed-bed]N\n\n" +
            "A₁_obv_i_4′: [x x x x x] {ú}la-al-[la-ga? {ú}im-ḫu-ur-lim?]\n" +
            "#lem: u; u; u; u; u; " +
            "+lalangu[(a leguminous vegetable)]N$lallaga\n\n" +
            "e_obv_15′–16′: {giš}ḪAŠḪUR [GIŠ.GI] — // [{ú}IGI-lim]\n" +
            "#lem: +hašhūru[apple (tree)]N$hašhūr; api[reed-bed]N;" +
            " imhur-līm['heals-a-thousand'-plant]N\n\n",
            ['LINELABEL'] + ['ID'] * 5 + ['NEWLINE'] +
            ['LEM', 'ID', 'SEMICOLON', 'ID', 'NEWLINE'] +
            ['SCORELABEL'] + ['ID'] * 7 + ['NEWLINE'] +
            ['LEM'] + ['ID', 'SEMICOLON'] * 5 + ['ID', 'NEWLINE'] +
            ['SCORELABEL'] + ['ID'] * 5 + ['NEWLINE'] +
            ['LEM'] + ['ID', 'SEMICOLON'] * 2 + ['ID', 'NEWLINE']
        )

    def test_composite(self):
        self.compare_tokens(
            "&Q002769 = SB Anzu 1\n" +
            "@composite\n" +
            "#project: cams/gkab\n" +
            "1.   bi#-in šar da-ad-mi šu-pa-a na-ram {d}ma#-mi\n" +
            "&Q002770 = SB Anzu 2\n" +
            "#project: cams/gkab\n" +
            "1.   bi-riq ur-ha šuk-na a-dan-na\n",
            ["AMPERSAND", "ID", "EQUALS", "ID", "NEWLINE"] +
            ['COMPOSITE', 'NEWLINE'] +
            ["PROJECT", "ID", "NEWLINE"] +
            ["LINELABEL"] + ['ID'] * 6 + ['NEWLINE'] +
            ["AMPERSAND", "ID", "EQUALS", "ID", "NEWLINE"] +
            ["PROJECT", "ID", "NEWLINE"] +
            ["LINELABEL"] + ['ID'] * 4 + ["NEWLINE"]
        )

    def test_translated_composite(self):
        self.compare_tokens(
            "&Q002769 = SB Anzu 1\n" +
            "@composite\n" +
            "#project: cams/gkab\n" +
            "1.   bi#-in šar da-ad-mi šu-pa-a na-ram {d}ma#-mi\n" +
            "@translation labeled en project\n" +
            "@(1) English\n"
            "&Q002770 = SB Anzu 2\n" +
            "#project: cams/gkab\n" +
            "1.   bi-riq ur-ha šuk-na a-dan-na\n",
            ["AMPERSAND", "ID", "EQUALS", "ID", "NEWLINE"] +
            ['COMPOSITE', 'NEWLINE'] +
            ["PROJECT", "ID", "NEWLINE"] +
            ["LINELABEL"] + ['ID'] * 6 + ['NEWLINE'] +
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE"] +
            ["OPENR", "ID", "CLOSER", "ID", "NEWLINE"] +
            ["AMPERSAND", "ID", "EQUALS", "ID", "NEWLINE"] +
            ["PROJECT", "ID", "NEWLINE"] +
            ["LINELABEL"] + ['ID'] * 4 + ["NEWLINE"]
        )

    def test_equalbrace(self):
        self.compare_tokens(
            "@tablet\n" +
            "@reverse\n" +
            "2'.    ITI# an-ni-u2#\n" +
            "={    ur-hu\n",
            ['TABLET', "NEWLINE"] +
            ["REVERSE", "NEWLINE"] +
            ["LINELABEL"] + ['ID'] * 2 + ["NEWLINE"] +
            ["EQUALBRACE", "ID", "NEWLINE"]
        )

    def test_multilingual_interlinear(self):
        self.compare_tokens(
            "@tablet\n" +
            "@obverse\n" +
            "1. dim₃#-me-er# [...]\n" +
            "#lem: diŋir[deity]N; u\n" +
            "== %sb DINGIR-MEŠ GAL#-MEŠ# [...]\n" +
            "#lem: ilū[god]N; rabûtu[great]AJ; u\n" +
            "# ES dim₃-me-er = diŋir\n" +
            "|| A o ii 15\n",
            ['TABLET', "NEWLINE"] +
            ["OBVERSE", "NEWLINE"] +
            ["LINELABEL"] + ['ID'] * 2 + ["NEWLINE"] +
            ["LEM"] + ["ID", "SEMICOLON"] + ["ID"] + ["NEWLINE"] +
            ["MULTILINGUAL", "ID"] + ["ID"] * 3 + ["NEWLINE"] +
            ["LEM"] + ["ID", "SEMICOLON"] * 2 + ["ID"] + ["NEWLINE"] +
            ["COMMENT", "ID", "NEWLINE"] +
            ["PARBAR", "ID", "ID", "ID", "ID", "NEWLINE"]
        )

    def test_strict_in_parallel(self):
        self.compare_tokens(
            "@translation parallel en project\n" +
            "$ reverse blank",
            ["TRANSLATION", "PARALLEL", "ID", "PROJECT", "NEWLINE"] +
            ["DOLLAR", "ID"]
        )

    def test_loose_in_labeled(self):
        self.compare_tokens(
            "@translation labeled en project\n" +
            "$ (Break)\n" +
            "@(r 2) I am\n\n",
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE"] +
            ["DOLLAR", "ID", "NEWLINE"] +
            ["OPENR", "ID", "ID", "CLOSER", "ID", "NEWLINE"]
        )

    def test_strict_in_labelled_parallel(self):
        self.compare_tokens(
            "@translation labeled en project\n" +
            "$ reverse blank",
            ["TRANSLATION", "LABELED", "ID", "PROJECT", "NEWLINE"] +
            ["DOLLAR", "ID"]
        )

    def test_strict_as_loose_in_translation(self):
        self.compare_tokens(
            "@translation parallel en project\n" +
            "$ Continued in text no. 2\n",
            ["TRANSLATION", "PARALLEL", "ID", "PROJECT", "NEWLINE"] +
            ["DOLLAR", "ID", "NEWLINE"]
        )

    def test_punctuated_translation(self):
        self.compare_tokens(
            "@translation parallel en project\n" +
            "1. 'What is going on?', said the King!\n",
            ["TRANSLATION", "PARALLEL", "ID", "PROJECT", "NEWLINE"] +
            ["LINELABEL", "ID", "NEWLINE"],
            [None, None, "en", None, None] +
            ["1", "'What is going on?', said the King!", None]
        )

    def test_translation_note(self):
        self.compare_tokens(
            "@translation parallel en project\n" +
            "@reverse\n" +
            "#note: reverse uninscribed\n",
            ["TRANSLATION", "PARALLEL", "ID", "PROJECT", "NEWLINE"] +
            ["REVERSE", "NEWLINE"] +
            ["NOTE", "ID", "NEWLINE"]
        )

    def test_equals_in_translation_note(self):
        self.compare_tokens(
            "@translation parallel en project\n" +
            "@reverse\n" +
            '#note: The CAD translation šarriru = "humble",\n',
            ["TRANSLATION", "PARALLEL", "ID", "PROJECT", "NEWLINE"] +
            ["REVERSE", "NEWLINE"] +
            ["NOTE", "ID", "NEWLINE"]
            )

    def test_note_ended_by_strucuture(self):
        self.compare_tokens(
            "@translation parallel en project\n" +
            "@obverse\n" +
            '#note: The CAD translation šarriru = "humble",\n' +
            '@reverse',
            ["TRANSLATION", "PARALLEL", "ID", "PROJECT", "NEWLINE"] +
            ["OBVERSE", "NEWLINE"] +
            ["NOTE", "ID", "NEWLINE"] +
            ["REVERSE"]
        )

    def test_milestone(self):
        self.compare_tokens(
            "@tablet\n" +
            "@obverse\n" +
            "@m=locator catchline\n" +
            "16'. si-i-ia-a-a-ku\n",
            ["TABLET", "NEWLINE",
             "OBVERSE", "NEWLINE",
             "M", "EQUALS", "ID", "NEWLINE",
             "LINELABEL", "ID", "NEWLINE"]
        )

    def test_include(self):
        self.compare_tokens(
            "@tablet\n" +
            "@obverse\n" +
            "@include dcclt:P229061 = MSL 07, 197 V02, 210 V11\n",
            ["TABLET", "NEWLINE",
             "OBVERSE", "NEWLINE",
             "INCLUDE", "ID", 'EQUALS', 'ID', "NEWLINE"]
        )
