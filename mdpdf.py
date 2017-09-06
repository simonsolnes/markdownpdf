#!/usr/bin/env python3
import sys
import os.path
import re

'''
To do:
- commandline
    - flags
- spans
    - citations
    - links
- blocks
    - quote
    - image
    - lists
    - code
- bibliography
'''

def conv_span(text):
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

    return ''.join(retval)

def conv_title(text):
    level = len(re.search('#*', text).group())
    subs = ''.join(['sub' for i in range(level - 1)])
    return '\\' + subs + 'section{' + conv_span(text[level + 1:]) + '}'

def conv_document(path):
    tex = []
    with open(path, 'r') as md_doc:
        skip = False
        for line in md_doc:
            text = line.rstrip('\n')
            if text == '``' and skip:
                skip = not skip
                continue
            elif skip:
                tex.append(text)
            elif text == '``latex':
                skip = True
                continue
            elif len(text) > 0:
                if text[0] is '#':
                    tex.append(conv_title(text))
                else:
                    tex.append(conv_span(text))

    return tex

def uses_bibliography(md_path):
    return False
def gen_ref(md_path):
    pass

if __name__ == '__main__':

    if len(sys.argv) != 3 or sys.argv[1] in ['-h', '-H', 'help']:
        print('usage:\n./mdpdf.py [input md] [header file]')
        exit()

    md_path = sys.argv[1]
    header_path = sys.argv[2]
    output_name = sys.argv[1].split('.')[0]

    debug_mode = False

    # User errors
    if not os.path.isfile(md_path):
        print('markdown document doesn\'t exist')
        exit()
    if not os.path.isfile(header_path):
        print('header document doesn\'t exist')
        exit()
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
    if debug_mode:
        exit(0)

    for i in ['.aux', '.log', '.toc', '.out', '.bbl', '.bcf', '.blg', '.dvi', '.run.xml', '-blx.bib', '.bib']:
        try:
            os.system('rmtrash ' + output_name + i + ' >> /dev/null')
        except:
            os.system('rm -f ' + output_name + i)
