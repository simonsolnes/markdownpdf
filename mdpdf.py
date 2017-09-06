#!/usr/bin/env python3
import sys
import os.path
import re

'''
To do:
- spans
    - citations
    - links
    - escape characters in latex
        - https://stackoverflow.com/questions/13655392/python-insert-a-character-into-a-string#13655397
        - '&%$#_{}~^\\'
- blocks
    - quote
        - nested quotes
    - image
    - lists
        - latex description lists
    - code
    - tables
        - text aligning
- bibliography
- title formatting
'''

def conv_span(text):
    if len(text) < 1:
        return ''
    def split_text(text, beg, end):
        retval = [item.split(beg) for item in text.split(end)]
        retval =  [word for sublist in retval for word in sublist]
        return retval.insert(0, '') if text[:2] is beg else retval
    def conv_format(text, find, beg = '', end = ''):
        retval = []
        for idx, item in enumerate(text.split(find)):
            retval.append(item)
            retval.append(beg) if idx % 2 == 0 else retval.append(end)
        return ''.join(retval[:-1])

    tex_split = split_text(text, '`$', '$`')

    retval = []
    for idx, part in enumerate(tex_split):
        if idx % 2 == 0:
            tmp = part
            tmp = conv_format(tmp, '**', '\\textbf{', '}')
            tmp = conv_format(tmp, '*', '\\textit{', '}')
            tmp = conv_format(tmp, '`', '\\texttt{', '}')
            retval.append(tmp)
        else:
            retval.append(part)

    # escape chars here
    return ''.join(retval)

def conv_list(lines):
    pass
def conv_quote(lines):
    pass
def conv_table(lines):
    pass
def conv_image(lines):
    pass
def conv_code(lines):
    pass

def conv_document(path):

    def locate_end(contents, matchfunc, default):
        for idx, line in enumerate(contents):
            if matchfunc(line):
                return idx + default + 1
        return default
    tex = []
    md_doc = open(path, 'r')
    lines = [item.rstrip('\n') for item in md_doc.readlines()]
    i = 0
    while i < len(lines):
        text = lines[i]
        end = i + 1
        # title
        if re.match('#+\s', text):
            level = len(re.match('#*', text).group())
            subs = ''.join(['sub' for i in range(level - 1)])
            block =  '\\' + subs + 'section{' + conv_span(text[level + 1:]) + '}'
        # latex
        elif re.match('``latex$', text):
            end = locate_end(lines[i + 1:], lambda x: x == '``', i)
            block = lines[i + 1: end]
        # list
        elif re.match('(\d\.|-|\*)\s', text):
            end = locate_end(lines[i + 1:], lambda x: x == '', i)
            block = conv_list(lines[i:end])
        else:
            block = conv_span(text)

        if isinstance(block, str): tex.append(block)
        if isinstance(block, list): tex += block
        i = end
    md_doc.close()

    return tex

def uses_bibliography(md_path):
    return False
def gen_ref(md_path):
    pass

def clear_files(output_name = '*'):
    ext = '.aux .log .toc .out .bbl .bcf .blg .dvi .bib .run.xml -blx.bib .bib .latex'
    for i in ext.split(' '):
        os.system('rm -f ' + output_name + i)

def parse_args(args):
    def print_usage():
        print('usage: mdpdf [markdown document] [header file]')
        print('optional flags: h: help, d: debug mode, c: rm latex files')
        exit(0)
    debug = False
    if len(args) == 3:
        md_path = args[1]
        header_path = args[2]
    elif len(args) == 4:
        if args[1] in ['-h', '-H', '--help', 'help']:
            print_usage()
        elif args[1] == '-d':
            debug = True
        md_path = args[2]
        header_path = args[3]
    elif len(args) == 2 and args[1] == '-c':
        clear_files()
        exit(0)
    else:
        print_usage()

    if not os.path.isfile(md_path):
        print('Markdown document doesn\'t exist')
        exit(0)
    if not os.path.isfile(header_path):
        print('Header document doesn\'t exist')
        exit(0)

    return debug, md_path, header_path

def main(md_path, header_path, output_name):
    uses_bib = uses_bibliography(md_path)

    with open(output_name + '.latex', 'w') as tex_doc, open(header_path, 'r') as header:
        for line in header:
            tex_doc.write(line) 
        if uses_bib:
            tex_doc.write('\\addbibresource{' + output_name + '.bib}\n')
        tex_doc.write('\\begin{document}\n')
        for line in conv_document(md_path):
            tex_doc.write(line + '\n')
        if uses_bib:
            tex_doc.write('\\printbibliography\n')
        tex_doc.write('\\end{document}\n')
    if uses_bib:
        with open(output_name + '.bib') as ref:
            for line in gen_ref(md_path):
                ref.write(line)
        os.system('latex ' + output_name + '.latex')
        os.system('bibtex ' + output_name + '.aux')
        os.system('latex ' + output_name + '.latex')

    os.system('pdflatex -interaction=batchmode ' + output_name + '.latex')
    

if __name__ == '__main__':
    debug, md_path, header_path = parse_args(sys.argv)
    output_name = md_path.split('.')[0]
    if debug:
        os.system('rm -f ' + output_name + '.pdf')
    main(md_path, header_path, output_name)
    if not debug:
        clear_files(output_name)
