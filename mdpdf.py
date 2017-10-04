#!/usr/bin/env python3
import sys
import os.path
import re
from pprint import pprint
import subprocess
'''
To do:
- bugs:
    - lists don't increment number
    - document cannot end with a list
- improvement
    - better latex debugging
- blocks
    - image
        ![caption text](path)
    - code
    - tables
        - text aligning
    - comments
    - newlines for double space

- future
    - reference style formatting links and footnotes
    - lists
        - newlines in list item
        - latex description lists
    - escape characters in latex
        - https://stackoverflow.com/questions/13655392/python-insert-a-character-into-a-string#13655397
        - '&%$#_{}~^\\'
    - nested quotes
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
    retval =  ''.join(retval)

    # links, footnotes, citations
    plaintexts = re.split('\[[^\]]+\]\([^\)]+\)', retval)
    references = re.findall('\[[^\]]+\]\([^\)]+\)', retval)
    tmp = ''
    for idx, item in enumerate(references):
        description = re.search('(?<=\[)[^\]]+', item).group()
        variable = re.search('(?<=\()[^\)]+', item).group()
        if description[0] != '@':
            tmp += plaintexts[idx] + '\\href{' + variable + '}{' + description + '}'
        elif description == '@fn':
            tmp += plaintexts[idx] + '\\footnote{' + variable + '}'
        elif description == '@cite':
            tmp += plaintexts[idx] + '\\cite{' + variable + '}'
    retval = tmp + plaintexts[-1]

    return retval
    
def conv_list(block):
	retval, idx = [], 0
	def conv_list_recurse(block, retval, idx):
		line = block[idx]
		l_level = len(re.match("\t*", line).group())
		l_type = re.match("\t*(\*|-|\d|\.)*(?=\s)", line)
		l_type = l_type.group().strip() if l_type else ""

		retval.append("\\begin{enumerate}") if re.match('\d', l_type[0]) else retval.append("\\begin{itemize}")
		retval.append("\\item " + conv_span(line[len('\t' * l_level + l_type):]))
		if idx + 1 < len(block) and l_level < len(re.match("\t*", block[idx + 1]).group()):
			idx = conv_list_recurse(block, retval, idx+1) - 1
		retval.append("\\end{enumerate}") if re.match('\d', l_type) else retval.append("\\end{itemize}")
		return idx + 1

	while(idx < len(block)): 
		idx = conv_list_recurse(block, retval, idx)

	return retval
def conv_quote(block):
    block[0] = block[0][2:]
    block.insert(0, '\\begin{quote}')
    block.append('\\end{quote}')
    return block
    
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
    md_doc = open(path, 'r')
    lines = [item.rstrip('\n') for item in md_doc.readlines()]
    uses_title = re.match('\$', lines[0])
    if uses_title:
        title = lines[0][2:]
        lines = lines[1:]
    else:
        title = ''
    i, tex = 0, []
    uses_bib = False
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
        # bibliography
        elif re.match('``bib$', text):
            end = locate_end(lines[i + 1:], lambda x: x == '``', i)
            block = generate_references(lines[i + 1: end], path[:-3] + '.bib')
            uses_bib = True
        # list
        elif re.match('(\d\.|-|\*)\s', text):
            end = locate_end(lines[i + 1:], lambda x: x == '', i)
            block = conv_list(lines[i:end])
        # block quotes
        elif re.match('\>\040', text):
            end = locate_end(lines[i + 1:], lambda x: x == '', i)
            block = conv_quote(lines[i:end])
        else:
            block = conv_span(text)

        if isinstance(block, str): tex.append(block)
        if isinstance(block, list): tex += block
        i = end
    md_doc.close()
    #NOTE: move this?

    return tex, uses_bib, uses_title, title

def generate_references(block, path):
    
    hastab = lambda x: x[:4] == '    ' or x[0] == '\t'
    entries = []
    i = 0
    while i < len(block):
        line = block[i]
        if not hastab(line):
            table = {}
            table['entry-name'] = re.search('^[^\[]+', line).group()
            table['entry-type'] = re.search('(?<=\[)[^\]]+', line).group()
            i += 1
            while i < len(block) and hastab(block[i]):
                table[re.search('[^\s:]+(?=:)', block[i]).group()] = re.sub('^\s*[^\s]*:\s*', '', block[i])
                i += 1
            entries.append(table)
            continue
        i += 1
    with open(path, 'w') as f:
        for entry in entries:
            f.write('@' + entry['entry-type'] + '{' + entry['entry-name'] + ',\n')
            del entry['entry-type']
            del entry['entry-name']
            for key, val in entry.items():
                f.write('\t' + key + ' = {' + val + '},\n')
            f.write('}\n')
        
    return '\\printbibliography'

def gen_header(header_path, uses_title, title):
    header = open(header_path, 'r').readlines()
    if not uses_title:
        return header
    for idx, line in enumerate(header):
        if bool(re.search('\$title\$', line)):
            tmp = re.split('\$title\$', line)
            tmp.insert(1, title)
            header[idx] = ''.join(tmp)
            
    return header
    

def clear_files(output_name = '*'):
    ext = '.aux .log .toc .out .bbl .bcf .blg .dvi .bib .run.xml -blx.bib .bib .latex'
    for i in ext.split(' '):
        os.system('rm -f ' + output_name + i)

def parse_args(args):
    def print_usage():
        print('usage: mdpdf [markdown document]')
        print('optional flags: h: help, d: debug mode, c: rm latex files')
        exit(0)
    debug = False

    if len(args) == 2 and args[1] == '-c':
        clear_files()
        exit(0)

    if 'LATEX_HEADER' in os.environ:
        header_path = os.environ['LATEX_HEADER']
    else:
        print('Please path to latex header as the environment variable "LATEX_HEADER"')
        exit(1)

    if len(args) > 1 and args[1] in ['-h', '-H', '--help', 'help']:
        print_usage()

    if len(args) == 2:
        md_path = args[1]
    elif len(args) == 3:
        if args[1] != '-d':
            print_usage()
        debug = True
        md_path = args[2]
    else:
        print_usage()
        
    if not os.path.isfile(md_path):
        print('Markdown document doesn\'t exist')
        exit(1)
    if not os.path.isfile(header_path):
        print('Path to header document is broken. Document doesn\'t exist')
        exit(1)

    return debug, md_path, header_path

def parse(md_path, header_path, output_name):
    tex_lines, uses_bib, uses_title, title = conv_document(md_path)
    os.system("echo | tr '\\n' '\\0' > log.txt")
    header = gen_header(header_path, uses_title, title)
    with open(output_name + '.latex', 'w') as tex_doc:
        for line in header:
            tex_doc.write(line) 
        if uses_bib:
            tex_doc.write('\\addbibresource{' + output_name + '.bib}\n')
        tex_doc.write('\\begin{document}\n')
        if uses_title:
            tex_doc.write('\\maketitle')
        for line in tex_lines:
            tex_doc.write(line + '\n')
        tex_doc.write('\\end{document}\n')
    if uses_bib:
        if os.system('pdflatex -interaction=nonstopmode ' + output_name + '.latex >> log.txt'):
            return 'first latex run'
        if os.system('bibtex ' + output_name + '.aux >> log.txt'):
            return 'bibtex run'
        if os.system('pdflatex -interaction=nonstopmode ' + output_name + '.latex >> log.txt'):
            return 'second latex run'

    if os.system('pdflatex -interaction=nonstopmode ' + output_name + '.latex >> log.txt'):
        return 'pdflatex run'
    return ''

def main():
    debug, md_path, header_path = parse_args(sys.argv)
    output_name = md_path.split('.')[0]

    errmsg = parse(md_path, header_path, output_name)
    if errmsg != '':
        print('There was an error with latex. Check log.txt')
        print('errmsg:', errmsg)
    else:
        os.system('rm -f log.txt')
        

    if not debug:
        clear_files(output_name)
if __name__ == '__main__':
    main()
