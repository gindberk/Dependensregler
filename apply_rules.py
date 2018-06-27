# coding=utf-8
"""Reading in Conll-files and applies rules for simplification on the trees"""

import tree_script
import codecs
import tree
global list_of_trees
list_of_trees = []

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def parse_trees(conll_file):
    """Opens conll file and returns it as a string."""
    tree = ""
    with open(conll_file) as f:
        for line in f:
            tree += line
    return(tree)

# The rules for simplification
scripts = ["temp_scripts/temp_script_p2a.txt",
           "temp_scripts/temp_script_prox.txt",
           "temp_scripts/temp_script_svo.txt",
           "temp_scripts/temp_script_split_a.txt",
           "temp_scripts/temp_script_split_k.txt",
           "temp_scripts/temp_script_split_r.txt",
           "temp_scripts/temp_script_qi.txt"]


def create_new_trees(scripts_filename, trees):
    """Applies the rules in the scripts on the trees."""
    new_trees = ''
    with open(scripts_filename, 'rt') as f:
        scripts = tree_script.parse_scripts(f.read().decode('utf-8'))
    for tree in read_trees(trees, scripts):
        # Run all the scripts on the tree
            tree = tree_script.run_tree_scripts(tree, scripts)
            new_trees += write_tree(tree)
    return new_trees


def read_trees(treeStr, scripts, errors='strict'):
    """Read the trees and check the format """
    tree_lines = treeStr.split('\n')
    node = 1
    forms, lemmas, cpostags, postags, feats, heads, deprels = \
        [], [], [], [], [], [], []

    for line_no, line in enumerate(tree_lines):
        try:
            line = line.decode('utf-8', errors).strip(u'\n')
            # On empty line, yield the tree (if the tree is not empty).
            if not line:
                if forms:
                    yield tree.Tree(forms, lemmas, cpostags, postags, feats,
                                    heads, deprels)
                    node = 1
                    forms, lemmas, cpostags, postags, feats, heads, deprels = \
                        [], [], [], [], [], [], []
                continue
            # Split the line and check the format.
            parts = line.split(u'\t')
            if len(parts) != 10:
                msg = 'expected 10 tab-separated fields, got %i'
                raise ValueError(msg % len(parts))
            if parts[0] != str(node):
                msg = 'field 0: expected %r, got %r'
                raise ValueError(msg % (str(node), parts[0]))
            for i, part in enumerate(parts):
                if part:
                    continue
                msg = 'field %i: empty'
                raise ValueError(msg % i)

            # Parse the fields.
            node += 1
            form = parts[1]
            lemma = parts[2]
            cpostag = parts[3]
            postag = parts[4]
            feat = parts[5].split(u'|')
            head = int(parts[6])
            deprel = parts[7]

            if parts[2] == u'_':
                lemma = u''
            if parts[5] == u'_':
                feat = []

            # Append the fields to the current tree.
            forms.append(form)
            lemmas.append(lemma)
            cpostags.append(cpostag)
            postags.append(postag)
            feats.append(feat)
            heads.append(head)
            deprels.append(deprel)

        # Catch all exceptions occurred while parsing, and report filename
        # and line number.
        except ValueError, e:
            msg = 'error while reading CoNLL file %r, line %i: %s'
            raise ValueError(msg % (treeStr, line_no, e))

    # On end-of-file, don't forget to yield the last tree.
    if forms:
        yield tree.Tree(forms, lemmas, cpostags, postags, feats, heads,
                        deprels)


def write_tree(tree):
    """Write a tree in CoNLL format. tree: a Tree."""
    written_tree = ''
    for i in range(len(tree)):
        node = i + 1
        form = tree.forms(node)
        lemma = tree.lemmas(node)
        cpostag = tree.cpostags(node)
        postag = tree.postags(node)
        feats = tree.feats(node)
        head = tree.heads(node)
        deprel = tree.deprels(node)

        if not _valid(form, empty_allowed=False):
            raise ValueError(u'invalid FORM: %r' % form)
        if not _valid(lemma, empty_allowed=True):
            raise ValueError(u'invalid LEMMA: %r' % lemma)
        if not _valid(cpostag, empty_allowed=False):
            raise ValueError(u'invalid CPOSTAG: %r' % cpostag)
        if not _valid(postag, empty_allowed=False):
            raise ValueError(u'invalid POSTAG: %r' % postag)
        if any(not _valid(feat, empty_allowed=False) for feat in feats):
            raise ValueError(u'invalid FEATS: %r' % feats)
        if not _valid(deprel, empty_allowed=False):
            raise ValueError(u'invalid DEPREL: %r' % deprel)

        #id = unicode(node)
        id = str(node)
        #lemma = lemma.encode('utf-8') or u'_'
        lemma = lemma or u'_'
        #head = unicode(head)
        head = str(head)
        feats = u'|'.join(feats).encode('utf-8') or u'_'
        #feats = u'|'.join(feats) or u'_'

        #parts = [id, form, lemma, cpostag, postag, feats, head, deprel]
        #file.write(u'\t'.join(parts) + u'\t_\t_\n')
        parts = [id, form, lemma, cpostag, postag, feats, head, deprel]

        written_tree += u'\t'.join(parts) + u'\t_\t_\n'
    written_tree += u'\n'
    return written_tree
    #file.write(u'\n')


def _valid(text, empty_allowed=False):
    """Return whether field in a tree (FORM, LEMMA, etc.) can be written to
    a CoNLL file."""

    # Whitespace is not allowed inside strings.
    for c in u'\t\n ':
        if c in text:
            return False

    # Required field must not be empty.
    if not empty_allowed and not text:
        return False

    # Can't encode underscores: underscore means 'empty' in CoNLL format.
    if empty_allowed and text == u'_':
        return False

    return True


def get_result(conll, name):
    """Runs the functions, and creates a conll file with the results"""
    scripts = ["temp_scripts/temp_script_p2a.txt",
               "temp_scripts/temp_script_prox.txt",
               "temp_scripts/temp_script_svo.txt",
               "temp_scripts/temp_script_split_a.txt",
               "temp_scripts/temp_script_split_k.txt",
               "temp_scripts/temp_script_split_r.txt",
               "temp_scripts/temp_script_qi.txt"]
    trees = parse_trees(conll)
    for script in scripts:
        print(script)
        trees = create_new_trees(script, trees)
    with open("ConLL/" + name + ".conllx", "w") as nyfil:
        nyfil.write(trees)
    return trees
