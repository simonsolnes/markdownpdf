# Markdown to PDF

Markdown to PDF converter that is not crappy.

## Usage

- Create an environment variable named 'LATEX_HEADER' with the path to your latex header. The latex header should everything in you standard file down to and excluding `\begin{document`. I bash this can be done by addding this line to `.bashrc`: `export LATEX_HEADER="full-path"`. If you don't have a header, or want to see what packages the converter uses, check out the minimal latex header in the repo.
- Make sure that you have python installed
- Make sure that you have the tex tools pdflatex, latex, bibtex 
- Optionally create an alias to the `mdpdf.py` file so that you can run it wherever in the filesystem

To compile a pdf from you markdown document, run this command:

```
$ python mdpdf.py [path to markdown document]
```

Important: The converter with overwrite any pdf with the same name as the markdown document.

## Standard markdown syntax

This are the standard markdown syntaxes the converter supports:

- Headers
- Italic (`*`-style)
- Bold (`**`-style)
- URLs
- Lists
- Blockquotes

If you are not familiar with markdown, check out [John Gruber Markdown syntax](https://daringfireball.net/projects/markdown/syntax)


## mdpdf Syntax

The good parts of this converter is the features that markdown doesn't support.

### Bibliography and citations

Citating a source:
	
	Lorem ipsum[@cite](my-book) dolor sit amet[@cite](source2)

Creating a bibliography with identifiers used in the example above (insert this at the bottom of your document):

	``bib
	my-book[book]:
		author: Simon Solnes
		title: Hey Wazzup
		year: 1947
	source2[online]:
		author:		Donald Knuth
    	title:		Knuth: Computers and Typesetting
    	url:		http://www-cs-faculty.stanford.edu/~uno/abcde.html
	``

In terms of [BibTeX format](http://www.bibtex.org/Format/) the mdpdf bibligraphy syntax looks like this:

	``bib
	entry[identifier-tag]:
		tag: tag-contents
	``

### Footnotes

Creating a footnote:
	
	Lorem impsum [@fn](text that will appear in the footnote)
	

### Latex code

Insert latex code inline:

	Lorem impsum `$\textbf{this is inline latex}$` dolor sit amet.

For latex math:

	Lorem impsum `$$\sum{n}$$` dolor sit amet

Latex blocks are formatted like this:

	``latex
	\subsection{Latex inside markdown}
	\begin{center}
		When $w^n=z$ is the $n$-th root of $z$\\
		$z=re^{i\theta}$ and $n$ is lots of weird maths. Then $z$, $n$-te bla bla bla $w_0 , w_1 , w_2 , ..., w_{n-1}$\\ 
		[0.5cm]
		$w_k =r^{\frac{1}{n}}e^{i\cfrac{\theta +2k\pi}{n}}$
	\end{center}
	``




## Future implementation

These features will hopefully be implemented in the future:

- Code blocks
- Images
- Tables
- Comments
- Reference style formatting links and footnotes
- Newlines in list items
- Recursive blockquotes
- Escaping special latex characters
- Being able to add tex code after `\begin{document}`
- Title formatting
- Latex description lists
- Lists with `•`
