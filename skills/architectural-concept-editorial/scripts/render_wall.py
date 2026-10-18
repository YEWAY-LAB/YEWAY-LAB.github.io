#!/usr/bin/env python3
"""Render an auditable wall of all pages in a source PDF; optional grayscale.
Usage: python scripts/render_wall.py deck.pdf --out wall.jpg --columns 2 --gray
"""
import argparse, math
from PIL import Image,ImageDraw,ImageFont,ImageOps
import fitz

def wall(path,out,columns=2,cell_width=1000,gray=False):
    doc=fitz.open(path)
    if not len(doc):raise ValueError('No PDF pages')
    ratio=doc[0].rect.height/doc[0].rect.width
    cell_h=int(cell_width*ratio)
    foot=34;rows=math.ceil(len(doc)/columns)
    image=Image.new('RGB',(columns*cell_width,rows*(cell_h+foot)),'#E7E7E6')
    draw=ImageDraw.Draw(image)
    for idx,p in enumerate(doc):
        pix=p.get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False)
        tile=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        tile.thumbnail((cell_width-18,cell_h-8))
        if gray:tile=ImageOps.grayscale(tile).convert('RGB')
        x=idx%columns*cell_width+(cell_width-tile.width)//2;y=idx//columns*(cell_h+foot)+2
        image.paste(tile,(x,y))
        draw.text((idx%columns*cell_width+12,idx//columns*(cell_h+foot)+cell_h+5),f'PAGE {idx+1:02d}',fill='#242424')
    image.save(out,quality=90)
    return len(doc)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('pdf');ap.add_argument('--out',required=True);ap.add_argument('--columns',type=int,default=2);ap.add_argument('--gray',action='store_true');a=ap.parse_args()
    print(f'Rendered {wall(a.pdf,a.out,a.columns,gray=a.gray)} pages -> {a.out}')
if __name__=='__main__':main()
