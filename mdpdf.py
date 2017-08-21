#!/usr/bin/env python3
import sys
import os.path

def conv_text(text):
    out = []
    for idx in range(len(text)):
        ch = text[idx]
        prv = text[idx - 1] if idx > 0 else ''
        nxt = text[idx + 1] if idx < len(text) - 1 else ''

        if ch is '*' and prv is not '*' and nxt is not '*':
            for chck in range(idx + 1, len(text)):
                chck_prv = text[chck - 1] if chck > 0 else ''
                chck_nxt = text[chck + 1] if chck < len(text) - 1 else ''
                if text[chck] is '*' and chck_prv is not '*' and chck_nxt is not '*':
                    mid = conv_text(text[idx + 1:chck])
                    end = conv_text(text[chck + 1:])
                    out.append(text[0:idx] + '\\textit{' + mid + '}' + end)
                    break
            break
        if ch is '*' and nxt is '*':
            for chck in range(idx + 1, len(text)):
                chck_nxt = text[chck + 1] if chck < len(text) - 1 else ''
                if text[chck] is '*' and chck_nxt is '*':
                    mid = conv_text(text[idx + 2:chck])
                    end = conv_text(text[chck + 2:])
                    out.append(text[0:idx] + '\\textbf{' + mid + '}' + end)
                    break
            break
        if ch is '`':
            for chck in range(idx + 1, len(text)):
                if text[chck] is '`':
                    mid = conv_text(text[idx + 1:chck])
                    end = conv_text(text[chck + 1:])
                    out.append(text[0:idx] + '\\texttt{' + mid + '}' + end)
                    break
            break
    if len(out) is 0: return text
    else: return ''.join(out)

def conv_title(text):
    level = 0
    for ch in text:
        if ch is '#': level += 1
        else: break
    pre = '\\'
    for lvl in range(level - 1):
        pre += 'sub'
    return pre + 'section{' + conv_text(text[level + 1:]) + '}'

def conv_document(path):
    tex_lines = []
    with open(path, 'r') as md_doc:
        for line in md_doc:
            text = line.rstrip()
            if len(text) < 1: continue

            # TitleBlock
            if line[0] is '#':
                block = conv_title(text)
            else:
                block = conv_text(text)

            # future:
                # BlockQuote
                # ImageBlock
                # ListBlock
            tex_lines.append(block)
    return tex_lines

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print('usage:\n./mdpdf.py [input md] [header file]')
        exit()

    md_path = sys.argv[1]
    header_path = sys.argv[2]

    # User errors
    if not os.path.isfile(md_path):
        print('markdown document doesn\'t exist')
        exit()
    if not os.path.isfile(header_path):
        print('header document doesn\'t exist')
        exit()

    with open('tmp.latex', 'w') as tex_doc, open(header_path, 'r') as header:
        for line in header:
            tex_doc.write(line) 
        tex_doc.write('\\begin{document}\n')
        for line in conv_document(md_path):
            tex_doc.write(line)
            tex_doc.write('\n')
        tex_doc.write('\\end{document}\n')

    os.system('pdflatex -interaction=batchmode tmp.latex')
    try:
        os.remove('tmp.latex')
        os.remove('tmp.aux')
        os.remove('tmp.log')
        os.remove('tmp.out')
    except:
        pass
