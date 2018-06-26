import copy
import re
import ply.lex
import ply.yacc
from ply.lex import TOKEN

#from dep_tregex.tree import *
#from dep_tregex.tree_pattern import *
#from dep_tregex.tree_action import *
#from dep_tregex.tree_state import *

import tree
import tree_pattern
import tree_action
import tree_state
import kor

## ----------------------------------------------------------------------------
#                             Script application

class TreeScript:
    """
    A TreePattern object coupled with several TreeAction objects.
    """

    def __init__(self, pattern, actions):
        self.pattern = pattern
        self.actions = actions

def run_tree_scripts(tree, scripts):
    """
    Apply tree scripts in a specific manner.

    - Scripts are applied sequentially: first script several times, second
      script several times, etc.
    - Any given script is only applied to "original" nodes of the tree.
      "Original" nodes are nodes  that existed at the time that script was
      first run.
    - Script is applied to each "original" node only once.
    - Script is applied until there are no "original" nodes left, to which
      that script hasn't been applied.
    """
    backrefs_map = {}
    state = tree_state.TreeState(copy.copy(tree), backrefs_map)
    match = False

    for script in scripts:
        # Reset the state
        state.unmark_all()
        for node in range(0, len(state.tree) + 1):
            state.mark(node)

        while True:
            backrefs_map.clear()

            # Find matching node.
            node = 0
            while node <= len(state.tree):
                if state.marked(node):
                    if script.pattern.match(state.tree, node, backrefs_map):
                        break
                node += 1

            # If no matching node, move on to the next script.
            if node == len(state.tree) + 1:
                break

            # Apply all actions.
            state.unmark(node)
            for action in script.actions:
                action.apply(state)
                match = True

            if match == True:
                print("It's a match!")


    if match == False:
        kor.list_of_trees.append(tree)

    #print(tree, match)
    return state.tree

## ----------------------------------------------------------------------------
#                              Script parser

class LexerError(ValueError):
    pass

class ParserError(ValueError):
    pass

class _TreeScriptParser:
    KEYWORDS = {
        'inf': 'INF',
        'pres': 'PRES',
        'pret': 'PRET',
        'sup': 'SUP',
        'and': 'AND',
        'or': 'OR',
        'not': 'NOT',
        'is_top': 'IS_TOP',
        'is_leaf': 'IS_LEAF',
        'form': 'FORM',
        'lemma': 'LEMMA',
        'cpostag': 'CPOSTAG',
        'postag': 'POSTAG',
        'feats': 'FEATS',
        'deprel': 'DEPREL',
        'can_head': 'CAN_HEAD',
        'can_be_headed_by': 'CAN_BE_HEADED_BY',
        'copy': 'COPY',
        'move': 'MOVE',
        'delete': 'DELETE',
        'add': 'ADD',
        'node': 'NODE',
        'group': 'GROUP',
        'before': 'BEFORE',
        'after': 'AFTER',
        'set': 'SET',
        'conj': 'CONJ',
        'set_head': 'SET_HEAD',
        'set_regex': 'SET_REGEX',
        'split': 'SPLIT',
        'try_set_head': 'TRY_SET_HEAD',
        'heads': 'HEADS',
        'headed_by': 'HEADED_BY'
        }

    TOKENS = [
        'ID',
        'STRING',
        'REGEX',
        'EQUALS',
        'COMMAND_SEP',
        'LPAREN',
        'RPAREN',
        'LBRACE',
        'RBRACE',
        'SEMICOLON',
        'BINARY_OP'
        ] + list(KEYWORDS.values())

    BINARY_OPS = {
        '.<--':tree_pattern.HasLeftChild,
        '-->.':tree_pattern.HasRightChild,
        '<--.':tree_pattern.HasRightHead,
        '.-->':tree_pattern.HasLeftHead,
        '.<-':tree_pattern.HasAdjacentLeftChild,
        '->.':tree_pattern.HasAdjacentRightChild,
        '<-.':tree_pattern.HasAdjacentRightHead,
        '.->':tree_pattern.HasAdjacentLeftHead,
        '>':tree_pattern.HasChild,
        '>>':tree_pattern.HasSuccessor,
        '<':tree_pattern.HasHead,
        '<<':tree_pattern.HasPredecessor,
        '$--':tree_pattern.HasLeftNeighbor,
        '$++':tree_pattern.HasRightNeighbor,
        '$-':tree_pattern.HasAdjacentLeftNeighbor,
        '$+':tree_pattern.HasAdjacentRightNeighbor
        }

    @classmethod
    def make_lexer(cls):
        tokens = cls.TOKENS
        t_ignore = ' \t'


        def track(t):
            # Compute position.
            start, end = t.lexer.lexmatch.span(0)
            line = t.lexer.lineno
            last_newline = t.lexer.lexdata.rfind(u'\n', 0, t.lexpos)
            col = (t.lexpos - last_newline)

            # Embed position into value.
            t.value = (t.value, (start, end, line, col))

        def t_ID(t):
            r'[_a-zA-Z][_a-zA-Z0-9]*'
            t.type = cls.KEYWORDS.get(t.value, 'ID')
            track(t)
            return t

        def t_STRING(t):
            r'[\"\'][^\"\']*[\"\']'
            t.value = t.value[1:-1]
            track(t)
            return t

        def t_REGEX(t):
            r'\/.*\/[ig]*'
            ignore_case = False
            anywhere = False
            while t.value[-1] in 'ig':
                if t.value[-1] == 'i':
                    ignore_case = True
                if t.value[-1] == 'g':
                    anywhere = True
                t.value = t.value[:-1]
            t.value = (t.value[1:-1], ignore_case, anywhere)
            track(t)
            return t

        def t_EQUALS(t):
            r'=='
            track(t)
            return t

        binary_ops = sorted(cls.BINARY_OPS.keys(), key=len, reverse=True)
        @TOKEN('|'.join(map(re.escape, binary_ops)))
        def t_BINARY_OP(t):
            track(t)
            return t

        def t_COMMAND_SEP(t):
            r'::'
            track(t)
            return t

        def t_LPAREN(t):
            r'\('
            track(t)
            return t

        def t_RPAREN(t):
            r'\)'
            track(t)
            return t

        def t_LBRACE(t):
            r'\{'
            track(t)
            return t

        def t_RBRACE(t):
            r'\}'
            track(t)
            return t

        def t_SEMICOLON(t):
            r';'
            track(t)
            return t

        t_ignore_COMMENT = r'\#.*'

        def t_newline(t):
            r'\n+'
            t.lexer.lineno += len(t.value)

        def t_error(t):
            line = t.lexer.lineno
            last_newline = t.lexer.lexdata.rfind(u'\n', 0, t.lexpos)
            col = (t.lexpos - last_newline)
            c = t.value[0:1]
            msg = '(at line %i, col %i) invalid character %r' % (line, col, c)
            raise LexerError(msg)

        #def t_error(t):
            #print("Illegal character '%s'" % t.value[0])
            #t.lexer.skip(1)


        return ply.lex.lex()

    @classmethod
    def make_parser(cls, start):
        tokens = cls.TOKENS

        def untrack(p):
            s, pos = [None], [None]
            for i in range(1, len(p)):
                s.append(p[i][0])
                pos.append(p[i][1])

            known_pos = filter(bool, pos)
            if not known_pos:
                p0_pos = None
            else:
                start_0, end_0, line_0, col_0 = known_pos[0]
                start_n, end_n, line_n, col_n = known_pos[-1]
                p0_pos = (start_0, end_n, line_0, col_0)
            pos[0] = p0_pos

            return s, pos

        def track(p, pos):
            p[0] = (p[0], pos[0])

        def p_error(p):
            if p:
                start, end, line, col = p.value[1]
                val = p.value[0]
                msg = '(at line %i, col %i) unexpected token %r' % \
                    (line, col, val)
            else:
                msg = 'unexpected end of file'
            raise ParserError(msg)

        def p_tree_scripts(p):
            """
            tree_scripts :
                         | tree_script tree_scripts
            """
            s, pos = untrack(p)
            if len(p) == 1:
                p[0] = []
            else:
                p[0] = [s[1]] + s[2]
            track(p, pos)

        def p_tree_pattern(p):
            """
            tree_pattern : ID
                         | ID condition
                         | LPAREN tree_pattern RPAREN
            """
            s, pos = untrack(p)
            if len(p) == 2:
                p[0] = tree_pattern.SetBackref(s[1], tree_pattern.NotRoot(tree_pattern.AlwaysTrue()))
            elif len(p) == 3:
                p[0] = tree_pattern.SetBackref(s[1], tree_pattern.NotRoot(s[2]))
            elif len(p) == 4:
                p[0] = s[2]
            p[0].pos = pos[0]
            track(p, pos)

        def p_tree_script(p):
            """
            tree_script : LBRACE tree_pattern COMMAND_SEP actions RBRACE
            """
            s, pos = untrack(p)
            p[0] = TreeScript(s[2], s[4])
            p[0].pos = pos[0]
            track(p, pos)

        def p_actions(p):
            """
            actions :
                    | action SEMICOLON actions
            """
            s, pos = untrack(p)
            if len(p) == 1:
                p[0] = []
            else:
                s[1].pos = pos[1]
                p[0] = [s[1]] + s[3]
            track(p, pos)

        def p_condition(p):
            """
            condition : condition_or
            """
            s, pos = untrack(p)
            p[0] = s[1]
            track(p, pos)

        def p_condition_or(p):
            """
            condition_or : condition_and or_conditions
            """
            s, pos = untrack(p)
            condition_and = s[1]
            or_conditions = s[2]

            if not or_conditions:
                p[0] = condition_and
            else:
                p[0] = tree_pattern.Or([condition_and] + or_conditions)
            track(p, pos)

        def p_or_conditions(p):
            """
            or_conditions :
                          | OR condition_and or_conditions
            """
            s, pos = untrack(p)
            if len(p) == 1:
                p[0] = []
            else:
                p[0] = [s[2]] + s[3]
            track(p, pos)

        def p_condition_and(p):
            """
            condition_and : condition_not and_conditions
            """
            s, pos = untrack(p)
            condition_not = s[1]
            and_conditions = s[2]

            if not and_conditions:
                p[0] = condition_not
            else:
                p[0] = tree_pattern.And([condition_not] + and_conditions)
            track(p, pos)

        def p_and_conditions(p):
            """
            and_conditions :
                           | AND condition_not and_conditions
            """
            s, pos = untrack(p)
            if len(p) == 1:
                p[0] = []
            else:
                p[0] = [s[2]] + s[3]
            track(p, pos)

        def p_condition_not(p):
            """
            condition_not : condition_op
                          | NOT condition_op
            """
            s, pos = untrack(p)
            if len(p) == 2:
                p[0] = s[1]
            else:
                p[0] = tree_pattern.Not(s[2])
            track(p, pos)

        def p_condition_op_parens(p):
            """
            condition_op : LPAREN condition RPAREN
            """
            s, pos = untrack(p)
            p[0] = s[2]
            track(p, pos)

        def p_condition_op_binary(p):
            """
            condition_op : BINARY_OP tree_pattern
            """
            s, pos = untrack(p)
            p[0] = cls.BINARY_OPS[s[1]](s[2])
            track(p, pos)

        def p_condition_op_equals(p):
            """
            condition_op : EQUALS ID
            """
            s, pos = untrack(p)
            p[0] = tree_pattern.EqualsBackref(s[2])
            track(p, pos)

        def p_condition_op_attr(p):
            """
            condition_op : attr string_condition
            """
            s, pos = untrack(p)
            if s[1] == 'feats':
                p[0] = tree_pattern.FeatsMatch(pred_fn=s[2])
            else:
                p[0] = tree_pattern.AttrMatches(attr=s[1], pred_fn=s[2])
            track(p, pos)

        def p_condition_op_is_top(p):
            """
            condition_op : IS_TOP
            """
            s, pos = untrack(p)
            p[0] = tree_pattern.IsTop()
            track(p, pos)

        def p_condition_op_is_leaf(p):
            """
            condition_op : IS_LEAF
            """
            s, pos = untrack(p)
            p[0] = tree_pattern.IsLeaf()
            track(p, pos)

        def p_condition_op_can_head(p):
            """
            condition_op : CAN_HEAD ID
            """
            s, pos = untrack(p)
            p[0] = tree_pattern.CanHead(s[2])
            track(p, pos)

        def p_condition_op_can_be_headed_by(p):
            """
            condition_op : CAN_BE_HEADED_BY ID
            """
            s, pos = untrack(p)
            p[0] = tree_pattern.CanBeHeadedBy(s[2])
            track(p, pos)

        def p_action_copy_move(p):
            """
            action : COPY selector ID where selector ID
                   | MOVE selector ID where selector ID
            """
            s, pos = untrack(p)
            kwargs = {
                'what': s[3],
                'sel_what': s[2],
                'where': s[4],
                'anchor': s[6],
                'sel_anchor': s[5]
                }

            if s[1] == 'copy':
                p[0] = tree_action.Copy(**kwargs)
            else:
                p[0] = tree_action.Move(**kwargs)
            track(p, pos)

        def p_action_delete(p):
            """
            action : DELETE selector ID
            """
            s, pos = untrack(p)
            p[0] = tree_action.Delete(what=s[3], sel_what=s[2])
            track(p, pos)

        def p_action_set(p):
            """
            action : SET attr ID STRING
                   | SET_REGEX attr ID REGEX
            """
            s, pos = untrack(p)
            if s[1] == 'set_regex':
                pattern, ignore_case, anywhere = s[4]
                r = tree_pattern.compile_regex(pattern, ignore_case, anywhere)
                p[0] = tree_action.SetRegex(s[3], '_' + s[2], r)
            else:
                if s[2] == 'feats':
                    newval = s[4].split(u'|')
                else:
                    newval = s[4]
                newval_fn = lambda x, newval=newval: newval
                p[0] = tree_action.MutateAttr(s[3], '_' + s[2], newval_fn)
            track(p, pos)

        def p_action_set_head(p):
            """
            action : SET_HEAD     ID HEADED_BY ID
                   | SET_HEAD     ID HEADS     ID
                   | TRY_SET_HEAD ID HEADED_BY ID
                   | TRY_SET_HEAD ID HEADS     ID
            """
            s, pos = untrack(p)
            raise_ = (s[1] == 'set_head')
            if s[3] == 'headed_by':
                node, head = s[2], s[4]
            else:
                node, head = s[4], s[2]
            p[0] = tree_action.SetHead(node=node, head=head, raise_on_invalid_head=raise_)
            track(p, pos)

        def p_action_group(p):
            """
            action : GROUP ID ID
            """
            s, pos = untrack(p)
            p[0] = tree_action.GroupTogether(s[2], s[3])
            track(p, pos)

        def p_action_split(p):
            """
            action : SPLIT where selector ID
                   | SPLIT where selector ID AND where selector ID
            """
            s, pos = untrack(p)
            if len(s) == 5:
                p[0] = tree_action.Split(s[4], s[3], s[2], None, None, None)
            else:
                p[0] = tree_action.Split(s[4], s[3], s[2], s[8], s[7], s[6])
            track(p, pos)

        def p_action_add(p):
            """
            action : ADD STRING where selector ID
            """
            s, pos = untrack(p)
            p[0] = tree_action.Add(s[2], s[3], s[5], s[4])
            track(p, pos)

        def p_action_conj(p):
            """
            action : CONJ ID con
            """
            s, pos = untrack(p)
            p[0] = tree_action.Conj(s[2], s[3])
            track(p, pos)

        def p_attr(p):
            """
            attr : FORM
                 | LEMMA
                 | CPOSTAG
                 | POSTAG
                 | FEATS
                 | DEPREL
            """
            s, pos = untrack(p)
            p[0] = {
                'form': 'forms',
                'lemma': 'lemmas',
                'cpostag': 'cpostags',
                'postag': 'postags',
                'feats': 'feats',
                'deprel': 'deprels'
                }[s[1]]
            track(p, pos)

        def p_con(p):
            """
            con : INF
                 | PRES
                 | PRET
                 | SUP
            """
            s, pos = untrack(p)
            p[0] = {
                'inf': 'inf',
                'pres': 'pres',
                'pret': 'pret',
                'sup': 'sup'
                }[s[1]]
            track(p, pos)

        def p_string_condition_str(p):
            """
            string_condition : STRING
            """
            s, pos = untrack(p)
            p[0] = lambda x, string=s[1]: x == string
            track(p, pos)

        def p_string_condition_regex(p):
            """
            string_condition : REGEX
            """
            s, pos = untrack(p)
            pattern, ignore_case, anywhere = s[1]
            r = tree_pattern.compile_regex(pattern, ignore_case, anywhere)
            p[0] = lambda x, r=r: r.search(x)
            track(p, pos)

        def p_selector(p):
            """
            selector : NODE
                     | GROUP
            """
            s, pos = untrack(p)
            if s[1] == 'node':
                p[0] = tree_action.NODE
            else:
                p[0] = tree_action.GROUP
            track(p, pos)

        def p_where(p):
            """
            where : BEFORE
                  | AFTER
            """
            s, pos = untrack(p)
            if s[1] == 'before':
                p[0] = tree.Tree.BEFORE
            else:
                p[0] = tree.Tree.AFTER
            track(p, pos)

        return ply.yacc.yacc(
            debug=0,
            write_tables=0,
            errorlog=ply.yacc.NullLogger()
            )

    def __init__(self, start):
        self.lexer = self.make_lexer()
        self.parser = self.make_parser(start)

    def parse(self, text):
        res, pos = self.parser.parse(text, lexer=self.lexer)
        return res

_TREE_SCRIPT_PARSER = None
_TREE_PATTERN_PARSER = None

def parse_pattern(text):
    """
    Parse a text, contatining a single tree pattern.
    Return TreePattern object.
    """

    # Compile parser on-demand.
    global _TREE_PATTERN_PARSER
    if _TREE_PATTERN_PARSER is None:
        _TREE_PATTERN_PARSER = _TreeScriptParser(start='tree_pattern')

    # Parse.
    return _TREE_PATTERN_PARSER.parse(text)

def parse_scripts(text):
    """
    Parse a text, contatining several tree scripts.
    Return list of TreeScript objects.
    """

    global _TREE_SCRIPT_PARSER
    if _TREE_SCRIPT_PARSER is None:
        _TREE_SCRIPT_PARSER = _TreeScriptParser(start='tree_scripts')

    # Parse.
    scripts = _TREE_SCRIPT_PARSER.parse(text)

    # Augment scripts, patterns and actions with their text.
    for script in scripts:
        # Augment script.
        start, end, line, col = script.pos
        script.text = text[start:end]

        # Augment pattern.
        start, end, line, col = script.pattern.pos
        script.pattern.text = text[start:end]

        # Augment actions.
        for action in script.actions:
            start, end, line, col = action.pos
            action.text = text[start:end]

    return scripts
