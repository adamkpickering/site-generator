# site-generator

This is a very simple static site generator using file hierarchies for structure
and markdown for content.

## To Do

- distinguish directories and files in generated links (perhaps put a slash after dir names?)
- generate a site map (I'm thinking it should look similar to the output of `tree`)
- use the python markdown module rather than calling markdown with subprocess module
- improve the CSS
- ansible deploy scripts
  - including a scan for broken links
- example website
- add instructions for installation
- add automatic creation of given destination directory
- add a monitor for file changes (also automate dev server) so that they show up in
  browser automatically

## How it Works

site-generator is for those who want the simplest possible website.
How to make a website:

1. Follow the instructions for installation.
1. Create a directory. This will be the root of your website.
1. Add markdown files for content, or directories.
   The structure of the root will be reflected in the URL structure of your website.
   If you want to add content to indexes, create `index.md` files in those directories.
1. Run `./compile.py` to compile the website.
1. More to come, once I've done the deployment part...
