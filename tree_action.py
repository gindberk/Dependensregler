#from dep_tregex.tree import *
#from dep_tregex.tree_pattern import *

import tree
import tree_pattern
import re
import kor
import konj
import codecs

## ----------------------------------------------------------------------------
#                                    Base

class TreeAction:
    """
    An object that represents a tree mutation.

    Instead of operating on just trees, it operates on TreeState, because we
    need to mutate the tree and backrefs_map jointly (see also TreeState
    description).
    """

    def get_backref(self, state, backref):
        """
        Return state.backrefs[backref] or raise TreeActionError if no such key.
        """
        if state.tree not in kor.list_of_trees:
            kor.list_of_trees.append(state.tree)

        if backref in state.backrefs_map:
            return state.backrefs_map[backref]

        msg = 'node %r was not matched in the pattern' % backref
        #self.error(msg)

    def error(self, msg):
        """
        Raise TreeActionError with given message.

        Augment exception with positional information if TreeAction has 'pos'
        and 'text' fields.
        """
        pos = getattr(self, 'pos', None)
        text = getattr(self, 'text', None)
        raise TreeActionError(msg, pos, text)

    def apply(self, state):
        """
        Apply mutation to the tree.
        """
        raise NotImplementedError()

class TreeActionError(Exception):
    """
    Exception which also holds position of tree action text in the original
    script file.
    """
    def __init__(self, msg, pos=None, text=None):
        self.msg = msg
        self.pos = pos
        self.text = text
        Exception.__init__(self, msg)

    def __str__(self):
        s = self.msg
        if self.pos:
            start, end, line, col = self.pos
            s = '(at line %i, col %i) %s' % (line, col, s)
        if self.text:
            lines = self.text.splitlines(False)
            lines = [u'    ' + line for line in lines]
            s = s + u'\n\n' + u'\n'.join(lines) + u'\n'
        return s

## ----------------------------------------------------------------------------
#                                  Utilities

# Selectors.
NODE = 'n'
GROUP = 'g'

def _gather(state, what, sel_what):
    """
    Return either a single node or node's group.

    what: node index
    sel_what: node selector, NODE or GROUP
    """
    if sel_what == NODE:
        return [what]
    else:
        return state.gather_group(what)

def _move(state, what_list, anchor, sel_anchor, where):
    """
    Move specified nodes (what_list) w.r.t specified anchor. Anchor might be
    a group of nodes, in which case a special behaviour is invoked.

    what_list: list of nodes to move; after the move, the nodes will end up
    next to each other

    anchor, sel_anchor: node (or a node group) to the right or to the left of
    which the moved nodes will go.

    where: Tree.BEFORE or Tree.AFTER
    """

    # If we're asked to move before/after the group, we select the
    # leftmost/rightmost node of anchor group as the anchor. Also, one of the
    # to-be-moved nodes can't be the anchor when we're moving before/after the
    # group.
    #
    # I believe that this is an intuitive behaviour (seriously :)
    # Consider for a moment, what would YOU do if you were asked to
    # "move group A before group B", and you find out that group A is a subset
    # of group B.
    if sel_anchor == GROUP:
        anchor_list = _gather(state, anchor, sel_anchor)
        anchor_list = set(anchor_list) - set(what_list)
        if not anchor_list:
            return

        if where == tree.Tree.BEFORE:
            anchor = min(anchor_list)
        else:
            anchor = max(anchor_list)

    # Invoke.
    state.move(what_list, anchor, where)

## ----------------------------------------------------------------------------
#                                   Actions

class Move(TreeAction):
    """
    Move a node (or a node group) before (or after) another node
    (or node group).
    """

    def __init__(self, what, anchor, sel_what, sel_anchor, where):
        """
        'what' and 'anchor' should be backreferences (i.e. strings).
        """
        self.what = what
        self.anchor = anchor
        self.sel_what = sel_what
        self.sel_anchor = sel_anchor
        self.where = where

    def apply(self, state):
        # Locate nodes.
        what = self.get_backref(state, self.what)
        anchor = self.get_backref(state, self.anchor)

        # Sanity checks.
        if what == 0:
            self.error("can't move root")
        if self.where == tree.Tree.BEFORE and anchor == 0:
            self.error("can't move something before root")

        # Gather indices & move.
        moved = _gather(state, what, self.sel_what)
        _move(state, moved, anchor, self.sel_anchor, self.where)

class Copy(TreeAction):
    """
    Copy a node (or a node group) before (or after) another node
    (or node group).
    """

    def __init__(self, what, anchor, sel_what, sel_anchor, where):
        """
        'what' and 'anchor' should be backreferences (i.e. 'unicode').
        """
        self.what = what
        self.anchor = anchor
        self.sel_what = sel_what
        self.sel_anchor = sel_anchor
        self.where = where

    def apply(self, state):
        # Locate nodes.
        what = self.get_backref(state, self.what)
        anchor = self.get_backref(state, self.anchor)

        # Sanity checks.
        if what == 0:
            self.error("can't move root")
        if self.where == tree.Tree.BEFORE and anchor == 0:
            self.error("can't move something before root")

        # Append.
        what = _gather(state, what, self.sel_what)
        state.tree.append_copy(what)
        num_new_words = len(what)
        new_num_words = len(state.tree)

        # Gather indices & move.
        moved = range(new_num_words - num_new_words + 1, new_num_words + 1)
        _move(state, moved, anchor, self.sel_anchor, self.where)

class Delete(TreeAction):
    """
    Delete a node (or a node group). Non-deleted descendants will be assigned
    to node's non-deleted parent.
    """

    def __init__(self, what, sel_what):
        """
        'what' should be a backreference (i.e. 'unicode').
        """
        self.what = what
        self.sel_what = sel_what

    def apply(self, state):
        # Locate nodes.
        deleted_node = self.get_backref(state, self.what)
        deleted_nodes = _gather(state, deleted_node, self.sel_what)

        # Sanity checks.
        if 0 in deleted_nodes:
            self.error("can't delete root")

        # Do it.
        state.delete(deleted_nodes)

class MutateAttr(TreeAction):
    """
    Modify 'attr'
    """

    def __init__(self, node, attr, newval_fn):
        """
        'node' should be a backreference (i.e. 'unicode').
        """
        self.node = node
        self.attr = attr
        self.newval_fn = newval_fn

    def apply(self, state):
        node = self.get_backref(state, self.node)
        if node == 0:
            self.error("can't set %r on root" % self.attr)
        # HACK: we use direct access to e.g. tree._forms.
        attr = getattr(state.tree, self.attr)
        attr[node - 1] = self.newval_fn(attr[node - 1])

class SetRegex(TreeAction):
    """
    Modify 'form'
    """

    def __init__(self, node, attr, r):
        """
        'node' should be a backreference (i.e. 'unicode').
        """
        self.node = node
        self.attr = attr
        self.r = r

    def apply(self, state):
        node = self.get_backref(state, self.node)
        if node == 0:
            self.error("can't set %r on root" % self.attr)
        # HACK: we use direct access to e.g. tree._forms.
        attr = getattr(state.tree, self.attr)
        string = attr[node - 1]
        if self.attr == "_feats":
            temp = ""
            for f in string:
                temp += f + "|"
            string = temp[:-1]
        newval = re.sub(self.r, '', string)
        newval_fn = lambda x, newval=newval: newval
        attr[node - 1] = newval_fn(attr[node - 1])

class SetHead(TreeAction):
    """
    Re-parent node. If impossible (i.e. if creates a cycle or disconnects
    a node):

    - If 'raise_on_invalid_head' was True, raises an exception.
    - Otherwise, does nothing.
    """

    def __init__(self, node, head, raise_on_invalid_head):
        """
        'node' and 'head' should be backreferences (i.e. 'unicode').
        """
        self.node = node
        self.head = head
        self.raise_on_invalid_head = raise_on_invalid_head

    def apply(self, state):
        node = self.get_backref(state, self.node)
        head = self.get_backref(state, self.head)

        # Sanity checks.
        if node == 0:
            self.error("can't set root's head")

        # Apply.
        can_set_head = head not in [node] + state.tree.children_recursive(node)
        if self.raise_on_invalid_head and not can_set_head:
            self.error("can't set head, invalid head")
        if can_set_head:
            state.tree.set_head(node=node, head=head)

class GroupTogether(TreeAction):
    """
    Group nodes together. When nodes A and B are grouped together, B is always
    included in "group of A" (whenever we gather that group for moving,
    deleting, etc.) and vice versa regardless of their parent-child
    relationship.
    """

    def __init__(self, node1, node2):
        """
        'node1' and 'node2' should be backreferences (i.e. 'unicode').
        """
        self.node1 = node1
        self.node2 = node2

    def apply(self, state):
        node1 = self.get_backref(state, self.node1)
        node2 = self.get_backref(state, self.node2)
        state.group_together(node1, node2)

class Split(TreeAction):

    def __init__(self, n1, sel_n1, where1, n2, sel_n2, where2):
        self.n1 = n1
        self.sel_n1 = sel_n1
        self.where1 = where1
        self.n2 = n2
        self.sel_n2 = sel_n2
        self.where2 = where2

    def apply(self, state):
        n1 = self.get_backref(state, self.n1)
        n1_ = sorted(_gather(state, n1, self.sel_n1))
        if self.where1 == '+':
            anchor1 = n1_[-1] + 1
        else:
            anchor1 = n1_[0]
        gathered = []

        if 0 in n1_:
            self.error("Not the root!")

        if self.n2 == None:
            for n in range(anchor1,len(state.tree._forms)):
                gathered.append(n)
        else:
            n2 = self.get_backref(state, self.n2)
            n2_ = sorted(_gather(state, n2, self.sel_n2))
            if self.where2 == '+':
                anchor2 = n2_[-1] + 1
            else:
                anchor2 = n2_[0]
            for n in range(anchor1, anchor2):
                gathered.append(n)

        nt = ([], [], [], [], [], [], [])

        for node in gathered:
            nt[0].append(state.tree.forms(node))
            nt[1].append(state.tree.lemmas(node))
            nt[2].append(state.tree.cpostags(node))
            nt[3].append(state.tree.postags(node))
            nt[4].append(state.tree.feats(node))
            nt[5].append(state.tree.heads(node))
            nt[6].append(state.tree.deprels(node))

        s = sorted(gathered)
        n0 = s[0] - 1

        for index, h in list(enumerate(nt[5])):
            if h - n0 >= len(s):
                nt[5][index] = len(s)
            elif h - n0 <= 0:
                nt[5][index] = 0
            else:
                nt[5][index] = h - n0

        state.delete(gathered)
        state.split(nt)

class Add(TreeAction):

    def __init__(self, what, where, anchor, sel_anchor):
        self.what = what
        self.where = where
        self.anchor = anchor
        self.sel_anchor = sel_anchor

    def apply(self, state):
        anchor = self.get_backref(state, self.anchor)
        head = state.tree.heads(anchor)

        gathered = _gather(state, anchor, self.sel_anchor)

        new = ([self.what], [self.what], ['_'], ['_'], [['_']], [anchor], ['_'])

        tree.Tree.append(state.tree, *new)

        #_move(state, moved, anchor, self.sel_anchor, self.where)

class Conj(TreeAction):

    def __init__(self, what, conj):
        self.what = what
        self.conj = conj
        self.attr = '_forms'

    def apply(self, state):
        what = self.get_backref(state, self.what)
        if what == 0:
            self.error("not the root!")
        attr = getattr(state.tree, self.attr)
        lemma = state.tree.lemmas(what)
        form = state.tree.forms(what)
        newval = konj.conjugate(lemma, self.conj, form)
        if isinstance(newval, str):
            newval = newval.decode('utf8')
        newval_fn = lambda x, newval=newval: newval
        attr[what - 1] = newval_fn(attr[what - 1])
